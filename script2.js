// Config
const CONFIG = {
  DIV_FACTOR: 1000000,
  MIN_MARKER_SIZE: 10,
  MAX_MARKER_SIZE: 60,
  MIN_ZOOM: 3,
  MAX_ZOOM: 18,
  PAUSE_TIME: 1000,
  TRANSITION_WINDOW: 10000,
  STATION_ID: "8600020",
  TIME: "13:19:40",
};

// API endpoints
const API = {
  STBOARD: window.location.protocol + "//" + window.location.host + "/" + "utils/trafic_data/" + CONFIG.STATION_ID + "/stboard.json",
  BUS_CLASSES: window.location.protocol + "//" + window.location.host + "/" + "bus_data.json",
  SHAPES: (i) => window.location.protocol + "//" + window.location.host + "/" + "utils/trafic_data/" + CONFIG.STATION_ID + "/shapes/" + i + ".json",
  RT_LINE: (i) => window.location.protocol + "//" + window.location.host + "/" + "utils/trafic_data/" + CONFIG.STATION_ID + "/lines/" + i + ".json"
};

// State management
const State = {
  stboardLoaded: false,
  busclassesLoaded: false,
  shapesLoaded: false,
  trainrtLoaded: false,
  json: {},
  json_shapes: [],
  trainrt: [],
  trainIds: [],
  stationName: '',
  busclassList: {},
  markers: [],
  routes: [],
  animationParams: [],
  map: null,
  zoom: -1,
  animationFrameId: null,
  backgroundInterval: null,
  newDayEpoch: 0,
  dummyTime: 0,
  currentView: 'departureBoard',
  selectedBusStops: [],
};

// Utility functions
const Utils = {
  toDanish: (text) => {
    const replacements = {
      '&#248;': 'ø', '&#230;': 'æ', '&#229;': 'å',
      '&#198;': 'Æ', '&#216;': 'Ø', '&#197;': 'Å'
    };
    return text.replace(/&#[0-9]{3};/g, match => replacements[match] || match);
  },

  extractUrlPart: (url) => {
    const regex = /ref=([^&]+)/;
    const match = url.match(regex);
    if (match) {
      const decoded = decodeURIComponent(match[1]);
      const parts = decoded.split('?');
      return parts[0];
    }
    return null;
  },

  calculateMarkerSize: (zoomLevel) => {
    return CONFIG.MIN_MARKER_SIZE + (CONFIG.MAX_MARKER_SIZE - CONFIG.MIN_MARKER_SIZE) * 
            (zoomLevel - CONFIG.MIN_ZOOM) / (CONFIG.MAX_ZOOM - CONFIG.MIN_ZOOM);
  },

  createArrowIcon: (text, size, idx) => {
    const busclass = State.busclassList[State.json.DepartureBoard.Departure[idx].line];
    return L.divIcon({
      html: `
        <div class="icon-container" style="width:${size}px;height:${size}px;">
          <img src="rotated_bus_icon.png" width="40" height="40" class="arrow-icon">
          <div class="marker-text ${busclass} route-number" style="font-size:${size/4}px;">${text}</div>
        </div>
      `,
      className: '',
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2]
    });
  },

  interpolate: (p1, p2, fraction) => {
    return [
      p1[0] + (p2[0] - p1[0]) * fraction,
      p1[1] + (p2[1] - p1[1]) * fraction
    ];
  },

  getBearing: (start, end, prevBearing) => {
    const startLat = start[0] * Math.PI / 180;
    const startLng = start[1] * Math.PI / 180;
    const endLat = end[0] * Math.PI / 180;
    const endLng = end[1] * Math.PI / 180;

    const dLng = endLng - startLng;

    const y = Math.sin(dLng) * Math.cos(endLat);
    const x = Math.cos(startLat) * Math.sin(endLat) -
              Math.sin(startLat) * Math.cos(endLat) * Math.cos(dLng);

    const bearing = Math.atan2(y, x) * 180 / Math.PI;
    
    const diff = bearing - prevBearing;
    const normalizedDiff = ((diff + 540) % 360) - 180;
    return prevBearing + normalizedDiff;
  },

  calculateDistance: (latlng1, latlng2) => {
    return State.map.distance(latlng1, latlng2);
  },

  timeToMs: (time) => {
    const [hours, minutes, seconds = 0] = time.split(':').map(Number);
    return hours * 3600000 + minutes * 60000 + seconds * 1000;
  }
};

// API calls
const API_Calls = {
  fetchStboard: async () => {
    const response = await fetch(API.STBOARD);
    State.json = await response.json();
    State.stationName = State.json.DepartureBoard.Departure[0].stop;
    State.trainIds = State.json.DepartureBoard.Departure.map(dep => Utils.extractUrlPart(dep.JourneyDetailRef.ref));
    State.stboardLoaded = true;
  },

  fetchBusClasses: async () => {
    const response = await fetch(API.BUS_CLASSES);
    State.busclassList = await response.json();
    State.busclassesLoaded = true;
  },

  fetchShapes: async () => {
    State.json_shapes = await Promise.all(State.trainIds.map(async (_, i) => {
      const response = await fetch(API.SHAPES(i));
      const data = await response.json();
      data[0] = data[0].map(v => ([v[0] / CONFIG.DIV_FACTOR, v[1] / CONFIG.DIV_FACTOR]));
      return data;
    }));
    State.shapesLoaded = true;
  },

  fetchRT: async () => {
    State.trainrt = await Promise.all(State.trainIds.map(async (_, i) => {
      const response = await fetch(API.RT_LINE(i));
      return await response.json();
    }));
    State.trainrtLoaded = true;
  }
};

// UI updates
const UI = {
  updateHeader: () => {
    document.getElementById("header_title").innerHTML = State.stationName;
  },

  createBars: () => {
    const barContainer = document.querySelector('.bar-container');
    State.json.DepartureBoard.Departure.forEach((dep, i) => {
      const newBar = barContainer.appendChild(document.createElement('div'));
      const icon = newBar.appendChild(document.createElement('div'));
      const busName = newBar.appendChild(document.createElement('div'));
      const rightbar = newBar.appendChild(document.createElement('div'));
      const platform = rightbar.appendChild(document.createElement('div'));
      const busDepartureDiv = rightbar.appendChild(document.createElement('div'));
      const departureTime = busDepartureDiv.appendChild(document.createElement('div'));
      const departureDelay = busDepartureDiv.appendChild(document.createElement('div'));
    
      newBar.classList.add('bar');
      icon.classList.add('busRouteNum');
      busName.classList.add('busRouteDest');
      rightbar.classList.add('rightboard');
      platform.classList.add('platformDiv');
      busDepartureDiv.classList.add('departureDiv');
      departureTime.classList.add('depTime');
      departureDelay.classList.add('originDelayTime');
    
      busName.textContent = dep.direction;
      if (dep.rtTime != undefined) {  
        departureTime.textContent = dep.rtTime;
        departureDelay.textContent = dep.time;
        departureDelay.style.display = 'block';
      } else {
        departureTime.textContent = dep.time;
      }

      if (dep.track != undefined) {
        platform.textContent = dep.track;
      }

      var busnum = dep.line;
      icon.textContent = busnum;
      icon.classList.add('bustype_default');

      if (i % 2 == 0) {
        newBar.style.backgroundColor = '#ffffff';
      }
      newBar.addEventListener('click', () => {
        window.location.href = 'utils/route-testing/route-test.html';
      });  
    });
  },

  updateBusIcons: () => {
    const icons = document.querySelectorAll('.busRouteNum');
    icons.forEach(icon => {
      const busnum = icon.textContent;
      const busclass = State.busclassList[busnum];
      icon.classList.add(busclass);
      icon.classList.add('route-number');
    });
  },

  renderBusStopList: () => {
    const busStopListContainer = document.createElement('div');
    busStopListContainer.className = 'bg-gray-100 p-4 shadow-md w-full';
    busStopListContainer.innerHTML = `
      <h2 class="text-2xl font-bold mb-4 text-center">Bus Stops</h2>
      <div id="bus-stops" class="space-y-2"></div>
    `;
    document.body.appendChild(busStopListContainer);

    const busStopsDiv = busStopListContainer.querySelector('#bus-stops');
    State.selectedBusStops.forEach(stop => {
      const stopDiv = document.createElement('div');
      stopDiv.className = 'flex items-center justify-between bg-white p-3 rounded-md shadow';
      stopDiv.innerHTML = `
        <div class="flex-grow">
          <p class="text-gray-800">${stop.name}</p>
        </div>
        <div class="flex-shrink-0 w-20 text-right">
          <div>
            <span class="font-semibold text-blue-600">
              ${stop.rtDepTime || stop.depTime}
            </span>
            ${stop.rtDepTime ? `
              <div class="text-xs text-red-500 line-through">
                ${stop.depTime}
              </div>
            ` : ''}
          </div>
        </div>
      `;
      busStopsDiv.appendChild(stopDiv);
    });
  },

  switchView: (view) => {
    const mapContainer = document.querySelector('.map-container');
    const barContainer = document.querySelector('.bar-container');
    const busStopListContainer = document.querySelector('.bg-gray-100.p-4.shadow-md.w-full');

    if (view === 'departureBoard') {
      if (mapContainer) mapContainer.style.display = 'block';
      if (barContainer) barContainer.style.display = 'flex';
      if (busStopListContainer) busStopListContainer.remove();
      State.currentView = 'departureBoard';
    } else if (view === 'busStopList') {
      if (mapContainer) mapContainer.style.display = 'none';
      if (barContainer) barContainer.style.display = 'none';
      UI.renderBusStopList();
      State.currentView = 'busStopList';
    }
  }
};

const TrainState = {
  NOT_DEPARTED: 'NOT_DEPARTED',
  READY_TO_DEPART: 'READY_TO_DEPART',
  MOVING: 'MOVING',
  STOPPING: 'STOPPING',
  ARRIVED: 'ARRIVED',
  JOURNEY_ENDED: 'JOURNEY_ENDED'
};

const AnimationUtils = {
  updateMarkerVisibility: (marker, isVisible) => {
    marker.setOpacity(isVisible ? 1 : 0);
  },

  updateMarkerPosition: (marker, point, bearing) => {
    marker.setLatLng(point);
    marker.getElement().querySelector('img').style.transform = `rotate(${bearing}deg)`;
  },

  updateMarkerIcon: (marker, line, size, idx) => {
    marker.setIcon(Utils.createArrowIcon(line, size, idx));
  },

  calculateNewPosition: (route, params, timePassed) => {
    let { index, distance, speed } = params;
    const distanceTraveled = speed * timePassed;
    distance += distanceTraveled;

    while (distance > 0 && index < route.length - 2) {
      const segmentLength = Utils.calculateDistance(route[index], route[index + 1]);
      if (distance <= segmentLength) break;
      distance -= segmentLength;
      index++;
    }

    const segmentLength = Utils.calculateDistance(route[index], route[index + 1]);
    const fraction = distance / (segmentLength + 0.0001);
    const point = Utils.interpolate(route[index], route[index + 1], fraction);
    const bearing = Utils.getBearing(route[index], route[index + 1], params.bearing);

    return { index, distance, point, bearing };
  },

  handleStopover: (params, currentTime) => {
    if (params.stopBegin === -1) {
      return { ...params, stopBegin: currentTime };
    } else if (currentTime - params.stopBegin > CONFIG.PAUSE_TIME) {
      return { ...params, stopBegin: -1, stops: params.stops + 1 };
    }
    return params;
  },

  isMarkerAtStop: (params, trainrt, shapes, nextStop) => {
    return nextStop < trainrt.JourneyDetail.Stop.length - 1 &&
           shapes[1][trainrt.JourneyDetail.Stop[nextStop].routeIdx][0] < params.index;
  },

  isMarkerBeforeDepartureTime: (trainrt, dummyTime) => {
    return Utils.timeToMs(trainrt.JourneyDetail.Stop[0].depTime) > dummyTime;
  }
};

// Map operations
const MapOperations = {
  initializeMap: () => {
    State.map = L.map('map').fitBounds([[57.071723, 10.054893],[57.009711, 9.820747]]);
    L.tileLayer("https://api.maptiler.com/maps/streets/{z}/{x}/{y}.png?key=KcoL2eYvC6zyiSr1kiT2", {}).addTo(State.map);
  },

  addStationMarker: () => {
    const station = State.trainrt[0].JourneyDetail.Stop.find(stop => stop.name === State.stationName);
    if (station) {
      L.marker([station.y / CONFIG.DIV_FACTOR, station.x / CONFIG.DIV_FACTOR], {icon: L.icon({
        iconUrl: 'pics\\busstop.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
      })
    }).addTo(State.map);
  }
},

createRoutes: () => {
  State.routes = State.json_shapes.map(shape => shape[0].map(v => ([v[1], v[0]])));
},

createMarkers: () => {
  State.markers = State.routes.map((route, i) => {
    const marker = L.marker(route[0], {
      icon: Utils.createArrowIcon(State.trainrt[i].JourneyDetail.JourneyLine.line, 50, i)
    }).addTo(State.map);
    
    marker.bindPopup(MapOperations.createPopupContent(i));
    
    marker.on('click', () => {
      State.selectedBusStops = State.trainrt[i].JourneyDetail.Stop.map(stop => ({
        name: stop.name,
        depTime: stop.depTime,
        rtDepTime: stop.rtDepTime
      }));
      UI.switchView('busStopList');
    });

    return marker;
  });
},

addPath: (id) => {
  if (State.map_shape) {
    State.map.removeLayer(State.map_shape);
  }

  const shape = State.json_shapes[id][0];
  const route_shape =  {
    "type": "Feature",
    "properties": {},
    "geometry": {
        "coordinates": shape,
        "type": "LineString"
    }
  };
  State.map_shape = L.geoJSON(route_shape, {
    style: {
        "color": "#333333",
        "weight": 5,
        "opacity": 0.8
    }
  }).addTo(State.map);
},

addBusStops: (id) => {
  const featureCollection = State.trainrt[id].JourneyDetail.Stop.map(item => ({
    type: "Feature",
    properties: {
        "name": item.name,
        "routeIdx": item.routeIdx,
        "arrTime": item.arrTime,
        "depTime": item.depTime,
        "$":""
    },
    geometry: {
        coordinates: [item.x / CONFIG.DIV_FACTOR, item.y / CONFIG.DIV_FACTOR],
        type: "Point"
    }
  }));
  const route_stops = {
    "type": "FeatureCollection",
    "features": featureCollection
  };
  State.map_routestops = L.geoJSON(route_stops, {
    pointToLayer: function (feature, latlng) {
      return L.marker(latlng, {
        icon: L.icon({
          iconUrl: 'pics\\busstop.png',
          iconSize: [32, 32],
          iconAnchor: [16, 32],
          popupAnchor: [0, -32]
        })
      });
    },
    onEachFeature: function (feature, layer) {
      layer.bindPopup(`
        <div class="bar">
          <div class="busRouteNum">${feature.properties.routeIdx}</div>
          <div class="busRouteDest">${feature.properties.name}</div>
          <div class="departureDiv">
            <div class="depTime">${feature.properties.depTime}</div>
            <div class="originDelayTime">${feature.properties.arrTime}</div>
          </div>
        </div>
      `);
    }
  }).addTo(State.map);
},

createPopupContent: (i) => {
  const dep = State.json.DepartureBoard.Departure[i];
  const prognosis = dep.rtTime || dep.time;
  const st_name = dep.stop;
  const delayedTime = dep.rtTime ? dep.time : '';
  const busClass = State.busclassList[dep.line] || '';
  const busLine = State.trainrt[i].JourneyDetail.JourneyLine.line;

  return `
    <div style="font-family: Arial, sans-serif; padding: 5px; min-width: 240px;">
      <div style="padding: 5px 0; margin-bottom: 10px; display: flex; justify-content: center; align-items: center;">
        <div class="busRouteNum ${busClass} route-number" style="
          font-size: 1.2em;
          min-width: 2.5em;
          height: 2.5em;
          margin-right: 10px;
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 0 0.3em;
          line-height: 1;
        ">
          ${busLine}
        </div>
        <div style="font-size: 1.1em; font-weight: bold;">
          ${dep.direction}
        </div>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div style="font-weight: bold; flex: 1; padding-right: 10px;">
          Afgang fra ${st_name}:
        </div>
        <div style="text-align: right; display: flex; flex-direction: column; justify-content: flex-start;">
          <div style="font-size: 1.2em; font-weight: bold;">
            ${prognosis}
          </div>
          ${delayedTime ? `
            <div style="font-size: 0.9em; color: #ff0000; text-decoration: line-through;">
              ${delayedTime}
            </div>
          ` : ''}
        </div>
      </div>
    </div>
  `;
},

calculateInitialPosition: (shapes, trainrt, id) => {
  const journey = trainrt.JourneyDetail.Stop;
  const shapes1 = State.json_shapes[id][0];
  const departure = State.json.DepartureBoard.Departure[id];

  const findInitialJourneyIndex = () => {
    const delay = departure.rtTime ? 
      Utils.timeToMs(departure.rtTime) - Utils.timeToMs(departure.time) : 0;

    for (let i = 1; i < journey.length - 1; i++) {
      if (!journey[i].depTime) continue;
      const departureTime = Utils.timeToMs(journey[i].depTime);
      if (departureTime + delay > State.dummyTime) {
        return {
          rawIndex: i - 1,
          index: Number(journey[i - 1].routeIdx),
          shapeIndex: State.json_shapes[id][1][journey[i - 1].routeIdx][0]
        };
      }
    }
    return {
      rawIndex: journey.length - 1,
      index: Number(journey[journey.length - 1].routeIdx),
      shapeIndex: shapes1.length - 1
    };
  };

  const calculateDistances = (startIndex) => {
    let totalDistance = 0;
    const distances = [];
    for (let i = startIndex; i < shapes1.length - 1; i++) {
      const segmentDistance = Utils.calculateDistance(L.latLng(shapes1[i]), L.latLng(shapes1[i + 1]));
      distances.push(segmentDistance);
      totalDistance += segmentDistance;
    }
    return { totalDistance, distances };
  };

  const calculateSpeed = (journeyIndex, totalDistance) => {
    if (journeyIndex.rawIndex >= journey.length - 1) {
      return { speed: 0, elapsedTime: 0 };
    }

    const delay = departure.rtTime ? 
      Utils.timeToMs(departure.rtTime) - Utils.timeToMs(departure.time) : 0;
    const totalTime = Utils.timeToMs(journey[journey.length - 1].arrTime) + delay -
      Utils.timeToMs(journey[journeyIndex.rawIndex].depTime) - 
      (CONFIG.PAUSE_TIME) * (journey.length - journeyIndex.rawIndex - 1);

    const speed = totalDistance / (totalTime || 0.00001);
    const elapsedTime = State.dummyTime - Utils.timeToMs(journey[journeyIndex.rawIndex].depTime) - delay;

    return { speed, elapsedTime };
  };

  const findCurrentPosition = (distances, distanceTraveled) => {
    let cumulativeDistance = 0;
    for (let i = 0; i < distances.length; i++) {
      if (cumulativeDistance + distances[i] > distanceTraveled) {
        return i;
      }
      cumulativeDistance += distances[i];
    }
    return distances.length - 1;
  };

  const journeyIndex = findInitialJourneyIndex();
  const { totalDistance, distances } = calculateDistances(journeyIndex.shapeIndex);
  const { speed, elapsedTime } = calculateSpeed(journeyIndex, totalDistance);
  const distanceTraveled = speed * elapsedTime;

  if (distanceTraveled >= totalDistance) {
    return { index: shapes1.length - 1, distance: 0, speed: 0, nextStop: shapes1.length - 1 };
  }

  const currentIndex = findCurrentPosition(distances, distanceTraveled);

  return {
    index: currentIndex + journeyIndex.shapeIndex,
    distance: 0,
    speed,
    nextStop: journeyIndex.rawIndex + 1
  };
},

animateMarkers: () => {
  const bounds = State.map.getBounds();
  const currentTime = Date.now() - State.newDayEpoch;
  const currentZoom = State.map.getZoom();
  const markerSize = Utils.calculateMarkerSize(currentZoom);
  let visibleMarkers = 0;

  State.routes.forEach((route, idx) => {
    let params = State.animationParams[idx];
    const marker = State.markers[idx];
    const trainrt = State.trainrt[idx];
    const shapes = State.json_shapes[idx];

    const currentTime1 = currentTime - params.stops * CONFIG.PAUSE_TIME;
    const nextStop = params.nextStop + params.stops;

    const state = MapOperations.determineTrainState(params, trainrt, shapes, nextStop, currentTime1);

    switch (state) {
      case TrainState.NOT_DEPARTED:
      case TrainState.JOURNEY_ENDED:
        if (params.visible) {
          AnimationUtils.updateMarkerVisibility(marker, false);
          params.visible = false;
        }
        break;

      case TrainState.READY_TO_DEPART:
      case TrainState.ARRIVED:
        if (!params.visible) {
          AnimationUtils.updateMarkerVisibility(marker, true);
          params.visible = true;
        }
        AnimationUtils.updateMarkerPosition(marker, route[params.index], params.bearing);
        visibleMarkers++;
        break;

      case TrainState.MOVING:
        const timePassed = (currentTime1 - params.lastUpdateTime);
        const { index, distance, point, bearing } = AnimationUtils.calculateNewPosition(route, params, timePassed);

        params = {
          ...params,
          index,
          distance,
          bearing,
          lastUpdateTime: currentTime1
        };

        const isVisible = bounds.contains(point);

        if (isVisible) {
          visibleMarkers++;
          AnimationUtils.updateMarkerPosition(marker, point, bearing);
        }

        if (isVisible !== params.visible) {
          AnimationUtils.updateMarkerVisibility(marker, isVisible);
          params.visible = isVisible;
        }
        break;

      case TrainState.STOPPING:
        params = AnimationUtils.handleStopover(params, currentTime1);
        visibleMarkers++;
        break;
    }

    if (currentZoom !== State.zoom) {
      AnimationUtils.updateMarkerIcon(marker, trainrt.JourneyDetail.JourneyLine.line, markerSize, idx);
      marker.getElement().querySelector('img').style.transform = `rotate(${params.bearing}deg)`;
    }

    State.animationParams[idx] = params;
  });

  State.zoom = currentZoom;

  MapOperations.scheduleNextAnimation(visibleMarkers > 0);
},

determineTrainState: (params, trainrt, shapes, nextStop, currentTime) => {
  const firstDepartureTime = Utils.timeToMs(trainrt.JourneyDetail.Stop[0].depTime);
  const lastArrivalTime = Utils.timeToMs(trainrt.JourneyDetail.Stop[trainrt.JourneyDetail.Stop.length - 1].arrTime);

  if (currentTime < firstDepartureTime - CONFIG.TRANSITION_WINDOW) {
    return TrainState.NOT_DEPARTED;
  } else if (currentTime >= firstDepartureTime - CONFIG.TRANSITION_WINDOW && currentTime < firstDepartureTime) {
    return TrainState.READY_TO_DEPART;
  } else if (currentTime > lastArrivalTime + CONFIG.TRANSITION_WINDOW) {
    return TrainState.JOURNEY_ENDED;
  } else if (currentTime >= lastArrivalTime && currentTime <= lastArrivalTime + CONFIG.TRANSITION_WINDOW) {
    return TrainState.ARRIVED;
  } else if (AnimationUtils.isMarkerAtStop(params, trainrt, shapes, nextStop)) {
    return TrainState.STOPPING;
  } else {
    return TrainState.MOVING;
  }
},

scheduleNextAnimation: (hasVisibleMarkers) => {
  if (hasVisibleMarkers) {
    if (State.backgroundInterval) {
      clearInterval(State.backgroundInterval);
      State.backgroundInterval = null;
    }
    State.animationFrameId = requestAnimationFrame(MapOperations.animateMarkers);
  } else {
    if (State.animationFrameId) {
      cancelAnimationFrame(State.animationFrameId);
      State.animationFrameId = null;
    }
    if (!State.backgroundInterval) {
      State.backgroundInterval = setInterval(MapOperations.animateMarkers, 500);
    }
  }
}
};

// Main execution
async function main() {
console.log("Starting the application...");
State.dummyTime = Utils.timeToMs(CONFIG.TIME);
State.newDayEpoch = Date.now() - State.dummyTime;
try {
  await Promise.all([
    API_Calls.fetchStboard(),
    API_Calls.fetchBusClasses()
  ]);

  UI.updateHeader();
  UI.createBars();
  UI.updateBusIcons();

  await Promise.all([
    API_Calls.fetchShapes(),
    API_Calls.fetchRT()
  ]);

  MapOperations.initializeMap();
  MapOperations.addStationMarker();
  MapOperations.createRoutes();
  MapOperations.createMarkers();

  State.animationParams = State.routes.map((route, i) => ({
    ...MapOperations.calculateInitialPosition(route, State.trainrt[i], i),
    stopBegin: -1,
    lastUpdateTime: Date.now() - State.newDayEpoch,
    visible: true,
    bearing: 0,
    stops: 0,
  }));

  MapOperations.animateMarkers();// Set up event listeners
  State.map.on('moveend zoomend', () => {
    if (State.animationFrameId) {
      cancelAnimationFrame(State.animationFrameId);
    }
    if (State.backgroundInterval) {
      clearInterval(State.backgroundInterval);
    }
    MapOperations.animateMarkers();
  });

  // Add event listener to switch back to departure board view
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && State.currentView === 'busStopList') {
      UI.switchView('departureBoard');
    }
  });

} catch (error) {
  console.error("An error occurred:", error);
}
}

// Run the application
main();
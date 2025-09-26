(function () {
    "use strict";

    if (typeof window === "undefined") {
        return;
    }

    var DEFAULT_CENTER = {
        lat: 7.1907,
        lng: 125.4553,
        zoom: 6,
    };

    var INITIALISED_FLAG = "obcMapInitialised";

    function markInitialised(container) {
        if (container) {
            container.dataset[INITIALISED_FLAG] = "true";
        }
    }

    function isInitialised(container) {
        return !!(container && container.dataset && container.dataset[INITIALISED_FLAG] === "true");
    }

    function resolveElement(value) {
        if (!value) {
            return null;
        }
        if (value instanceof HTMLElement) {
            return value;
        }
        if (typeof value === "string") {
            return document.getElementById(value);
        }
        return null;
    }

    function parseNumber(value) {
        if (value === null || value === undefined || value === "") {
            return null;
        }
        var parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : null;
    }

    function formatCoord(value) {
        return value !== null && value !== undefined
            ? Number(value).toFixed(6)
            : "";
    }

    function parseJsonScript(scriptId) {
        if (!scriptId) {
            return null;
        }
        var script = document.getElementById(scriptId);
        if (!script) {
            console.warn("Map initialisation skipped; missing script", scriptId);
            return null;
        }
        try {
            return JSON.parse(script.textContent);
        } catch (error) {
            console.error("Failed to parse JSON script", scriptId, error);
            return null;
        }
    }

    function createTileLayer(map, options) {
        var url = (options && options.url) || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
        var tileOptions = {
            attribution:
                "Map data © <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors",
            minZoom: 3,
            maxZoom: 18,
        };
        if (options && typeof options.minZoom === "number") {
            tileOptions.minZoom = options.minZoom;
        }
        if (options && typeof options.maxZoom === "number") {
            tileOptions.maxZoom = options.maxZoom;
        }
        if (options && options.attribution) {
            tileOptions.attribution = options.attribution;
        }
        return window.L.tileLayer(url, tileOptions).addTo(map);
    }

    function createMap(mapNode, dataset) {
        var lat = parseNumber(dataset.initialLat);
        if (lat === null) {
            lat = DEFAULT_CENTER.lat;
        }
        var lng = parseNumber(dataset.initialLng);
        if (lng === null) {
            lng = DEFAULT_CENTER.lng;
        }
        var zoom = parseNumber(dataset.initialZoom);
        if (zoom === null) {
            zoom = DEFAULT_CENTER.zoom;
        }

        var interactionOptions = {
            scrollWheelZoom: dataset.mode === "detail" ? false : true,
        };

        var map = window.L.map(mapNode, interactionOptions);
        map.setView([lat, lng], zoom);
        var minZoom = parseNumber(dataset.minZoom);
        if (minZoom === null) {
            minZoom = 3;
        }
        var maxZoom = parseNumber(dataset.maxZoom);
        if (maxZoom === null) {
            maxZoom = 18;
        }
        createTileLayer(map, {
            minZoom: minZoom,
            maxZoom: maxZoom,
        });
        return map;
    }

    function ensureMarker(map, markerRef, lat, lng, options) {
        if (!markerRef.marker) {
            markerRef.marker = window.L.marker([lat, lng], options || {});
            markerRef.marker.addTo(map);
        } else {
            markerRef.marker.setLatLng([lat, lng]);
        }
        if (markerRef.popupContent) {
            markerRef.marker.bindPopup(markerRef.popupContent);
        }
        return markerRef.marker;
    }

    function buildLookup(collection) {
        var lookup = new Map();
        if (!Array.isArray(collection)) {
            return lookup;
        }
        collection.forEach(function (item) {
            if (!item || item.id === undefined) {
                return;
            }
            lookup.set(String(item.id), item);
        });
        return lookup;
    }

    function findBestCoordinates(lookups, ids) {
        for (var i = 0; i < ids.length; i += 1) {
            var config = ids[i];
            if (!config || !config.id || !config.lookup) {
                continue;
            }
            var record = config.lookup.get(String(config.id));
            if (!record) {
                continue;
            }
            var lat = parseNumber(record.center_lat);
            var lng = parseNumber(record.center_lng);
            if (lat !== null && lng !== null) {
                return { lat: lat, lng: lng, zoom: config.zoom };
            }
        }
        return null;
    }

    function createCentroidFetcher(centroidUrl) {
        return function fetchCentroid(level, id) {
            if (!centroidUrl || !level || !id) {
                return Promise.resolve(null);
            }

            var url =
                centroidUrl +
                "?level=" + encodeURIComponent(level) +
                "&id=" + encodeURIComponent(id);

            return fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(function (response) {
                    if (!response.ok) {
                        return null;
                    }
                    return response.json();
                })
                .catch(function () {
                    return null;
                });
        };
    }

    function setupFormMap(container) {
        var mapNode = container.querySelector("[data-obc-map-target]");
        if (!mapNode) {
            return;
        }

        var map = createMap(mapNode, container.dataset);
        var markerHolder = { marker: null, manual: false };
        var isProgrammaticFieldUpdate = false;
        var centroidUrl = container.dataset.centroidUrl || "";
        var centroidRequestId = 0;
        var fetchCentroid = createCentroidFetcher(centroidUrl);

        var latField = document.getElementById(container.dataset.latField || "");
        var lngField = document.getElementById(container.dataset.lngField || "");

        function currentLatLng() {
            return {
                lat: parseNumber(latField ? latField.value : null),
                lng: parseNumber(lngField ? lngField.value : null),
            };
        }

        function updateMarkerFromFields(opts) {
            if (!latField || !lngField) {
                return;
            }
            if (isProgrammaticFieldUpdate) {
                markerHolder.manual = false;
                isProgrammaticFieldUpdate = false;
                if (latField) {
                    latField.dataset.manualOverride = "false";
                }
                if (lngField) {
                    lngField.dataset.manualOverride = "false";
                }
                return;
            }
            var coords = currentLatLng();
            if (coords.lat === null || coords.lng === null) {
                return;
            }
            markerHolder.manual = true;
            if (latField) {
                latField.dataset.manualOverride = "true";
            }
            if (lngField) {
                lngField.dataset.manualOverride = "true";
            }
            ensureMarker(map, markerHolder, coords.lat, coords.lng, opts);
            var focusZoom = parseNumber(container.dataset.focusZoom);
            if (focusZoom === null) {
                focusZoom = 14;
            }
            map.setView([coords.lat, coords.lng], focusZoom);
        }

        if (latField && lngField) {
            var initial = currentLatLng();
            if (initial.lat !== null && initial.lng !== null) {
                ensureMarker(map, markerHolder, initial.lat, initial.lng);
                markerHolder.manual = false;
            }

            var syncField = function () {
                updateMarkerFromFields();
            };
            latField.addEventListener("change", syncField);
            lngField.addEventListener("change", syncField);
            latField.addEventListener("input", syncField);
            lngField.addEventListener("input", syncField);
        }

        function placeMarker(lat, lng, zoom, respectExistingMarker) {
            if (lat === null || lng === null || !isFinite(lat) || !isFinite(lng)) {
                console.warn("Invalid coordinates provided:", lat, lng);
                return;
            }

            // Validate coordinates are within reasonable bounds
            if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
                console.warn("Coordinates out of bounds:", lat, lng);
                return;
            }

            if (respectExistingMarker && markerHolder.manual) {
                return;
            }

            map.setView([lat, lng], zoom);

            if (latField && lngField) {
                var shouldUpdateFields =
                    !respectExistingMarker ||
                    latField.value === "" ||
                    lngField.value === "" ||
                    !markerHolder.manual;
                if (shouldUpdateFields) {
                    isProgrammaticFieldUpdate = true;
                    latField.value = formatCoord(lat);
                    lngField.value = formatCoord(lng);
                    latField.dataset.manualOverride = "false";
                    lngField.dataset.manualOverride = "false";
                    ensureMarker(map, markerHolder, lat, lng);
                    markerHolder.manual = false;

                    // Trigger change events to ensure form validation
                    var changeEvent = new Event("change", { bubbles: true });
                    latField.dispatchEvent(changeEvent);
                    lngField.dispatchEvent(changeEvent);
                }
            } else {
                ensureMarker(map, markerHolder, lat, lng);
                markerHolder.manual = false;
            }
        }

        var locationData = parseJsonScript(container.dataset.locationScript);
        var lookups = {
            regions: buildLookup(locationData && locationData.regions),
            provinces: buildLookup(locationData && locationData.provinces),
            municipalities: buildLookup(locationData && locationData.municipalities),
            barangays: buildLookup(locationData && locationData.barangays),
        };

        function recenterFromSelections(respectExistingMarker) {
            var selectionHierarchy = [];
            var barangayField = document.getElementById(container.dataset.barangayField || "");
            var municipalityField = document.getElementById(container.dataset.municipalityField || "");
            var provinceField = document.getElementById(container.dataset.provinceField || "");
            var regionField = document.getElementById(container.dataset.regionField || "");

            selectionHierarchy.push({
                field: barangayField,
                level: "barangay",
                lookup: lookups.barangays,
                zoom: 15,
            });
            selectionHierarchy.push({
                field: municipalityField,
                level: "municipality",
                lookup: lookups.municipalities,
                zoom: 12,
            });
            selectionHierarchy.push({
                field: provinceField,
                level: "province",
                lookup: lookups.provinces,
                zoom: 9,
            });
            selectionHierarchy.push({
                field: regionField,
                level: "region",
                lookup: lookups.regions,
                zoom: 7,
            });

            var localBest = null;
            var fetchTarget = null;

            selectionHierarchy.forEach(function (entry) {
                if (!entry.field || !entry.field.value) {
                    return;
                }

                if (!fetchTarget) {
                    fetchTarget = {
                        level: entry.level,
                        id: entry.field.value,
                        zoom: entry.zoom,
                    };
                }

                if (!localBest) {
                    var record = entry.lookup.get(String(entry.field.value));
                    var lat = record ? parseNumber(record.center_lat) : null;
                    var lng = record ? parseNumber(record.center_lng) : null;
                    if (lat !== null && lng !== null) {
                        localBest = {
                            lat: lat,
                            lng: lng,
                            zoom: entry.zoom,
                        };
                    }
                }
            });

            if (localBest) {
                placeMarker(localBest.lat, localBest.lng, localBest.zoom, respectExistingMarker);
            }

            if (fetchTarget) {
                centroidRequestId += 1;
                var requestToken = centroidRequestId;
                fetchCentroid(fetchTarget.level, fetchTarget.id).then(function (payload) {
                    if (requestToken !== centroidRequestId) {
                        return;
                    }
                    if (!payload) {
                        console.warn("No coordinate data received for", fetchTarget.level, fetchTarget.id);
                        return;
                    }
                    if (!payload.has_location) {
                        console.info("No coordinates available for", fetchTarget.level, fetchTarget.id);
                        return;
                    }
                    if (markerHolder.manual) {
                        return;
                    }
                    if (payload.lat !== null && payload.lng !== null) {
                        var respectManual = respectExistingMarker || markerHolder.manual;
                        placeMarker(payload.lat, payload.lng, fetchTarget.zoom, respectManual);
                    }
                }).catch(function (error) {
                    console.error("Failed to fetch coordinates for", fetchTarget.level, fetchTarget.id, error);
                });
            }
        }

        ["regionField", "provinceField", "municipalityField", "barangayField"].forEach(function (key) {
            var fieldId = container.dataset[key];
            if (!fieldId) {
                return;
            }
            var field = document.getElementById(fieldId);
            if (!field) {
                return;
            }
            field.addEventListener("change", function () {
                markerHolder.manual = false;
                recenterFromSelections(false);
            });
        });

        recenterFromSelections(false);

        map.on("click", function (event) {
            var lat = event.latlng.lat;
            var lng = event.latlng.lng;
            ensureMarker(map, markerHolder, lat, lng);
            markerHolder.manual = true;
            if (latField) {
                latField.value = formatCoord(lat);
                latField.dataset.manualOverride = "true";
                latField.dispatchEvent(new Event("change", { bubbles: true }));
            }
            if (lngField) {
                lngField.value = formatCoord(lng);
                lngField.dataset.manualOverride = "true";
                lngField.dispatchEvent(new Event("change", { bubbles: true }));
            }
        });
    }

    function setupDetailMap(container) {
        var mapNode = container.querySelector("[data-obc-map-target]");
        if (!mapNode) {
            return;
        }

        var dataset = container.dataset;
        var hasLocation = dataset.hasLocation === "true";
        if (!dataset.initialLat || !dataset.initialLng) {
            var fallbackLat = parseNumber(dataset.fallbackLat);
            var fallbackLng = parseNumber(dataset.fallbackLng);
            var fallbackZoom = parseNumber(dataset.fallbackZoom);

            if (fallbackLat !== null && fallbackLng !== null) {
                dataset.initialLat = String(fallbackLat);
                dataset.initialLng = String(fallbackLng);
                if (fallbackZoom !== null) {
                    dataset.initialZoom = String(fallbackZoom);
                }
            }
        }

        if (parseNumber(dataset.initialLat) === null || parseNumber(dataset.initialLng) === null) {
            dataset.initialLat = String(DEFAULT_CENTER.lat);
            dataset.initialLng = String(DEFAULT_CENTER.lng);
            if (!dataset.initialZoom) {
                dataset.initialZoom = String(DEFAULT_CENTER.zoom);
            }
        }

        var map = createMap(mapNode, dataset);
        var lat = parseNumber(dataset.initialLat);
        var lng = parseNumber(dataset.initialLng);
        if (lat === null || lng === null) {
            return;
        }
        if (!hasLocation) {
            return;
        }
        ensureMarker(map, { marker: null, popupContent: dataset.popupContent }, lat, lng);
    }

    function setupMultiMap(container) {
        var mapNode = container.querySelector("[data-obc-map-target]");
        if (!mapNode) {
            return;
        }

        var dataset = container.dataset;
        var map = createMap(mapNode, dataset);
        var markerLayer = window.L.layerGroup().addTo(map);

        var selectionField = document.getElementById(dataset.selectionField || "");
        var barangayField = document.getElementById(dataset.barangayField || "");
        var municipalityField = document.getElementById(dataset.municipalityField || "");
        var provinceField = document.getElementById(dataset.provinceField || "");
        var regionField = document.getElementById(dataset.regionField || "");

        var communityData = parseJsonScript(dataset.source) || [];
        var communityLookup = buildLookup(communityData);

        var locationData = parseJsonScript(dataset.locationScript);
        var lookups = {
            regions: buildLookup(locationData && locationData.regions),
            provinces: buildLookup(locationData && locationData.provinces),
            municipalities: buildLookup(locationData && locationData.municipalities),
            barangays: buildLookup(locationData && locationData.barangays),
        };

        function determineCommunityCoordinates(record) {
            if (!record) {
                return null;
            }
            if (
                record.has_location === false &&
                !record.barangay_id &&
                !record.municipality_id &&
                !record.province_id &&
                !record.region_id
            ) {
                return null;
            }
            var lat = parseNumber(record.latitude);
            var lng = parseNumber(record.longitude);
            if (lat !== null && lng !== null) {
                return { lat: lat, lng: lng, zoom: 14 };
            }
            return findBestCoordinates(lookups, [
                { id: record.barangay_id, lookup: lookups.barangays, zoom: 15 },
                { id: record.municipality_id, lookup: lookups.municipalities, zoom: 12 },
                { id: record.province_id, lookup: lookups.provinces, zoom: 9 },
                { id: record.region_id, lookup: lookups.regions, zoom: 7 },
            ]);
        }

        function renderSelectedCommunities() {
            markerLayer.clearLayers();
            if (!selectionField) {
                return;
            }
            var selectedOptions = Array.from(selectionField.options).filter(function (option) {
                return option.selected;
            });
            var bounds = [];
            selectedOptions.forEach(function (option) {
                var record = communityLookup.get(option.value);
                var coords = determineCommunityCoordinates(record);
                if (!coords) {
                    return;
                }
                var marker = window.L.marker([coords.lat, coords.lng]).addTo(markerLayer);
                var title = record ? record.name : option.text;
                marker.bindPopup(
                    "<div class=\"text-sm\"><strong>" +
                        title +
                        "</strong><br/><span class=\"text-gray-500\">" +
                        (record && record.full_path ? record.full_path : "Selected OBC location") +
                        "</span></div>"
                );
                bounds.push([coords.lat, coords.lng]);
            });
            if (bounds.length === 1) {
                map.setView(bounds[0], 14);
            } else if (bounds.length > 1) {
                map.fitBounds(bounds, { padding: [24, 24] });
            }
        }

        function recenterFromCoverage() {
            var ids = [];
            if (barangayField && barangayField.value) {
                ids.push({ id: barangayField.value, lookup: lookups.barangays, zoom: 15 });
            }
            if (municipalityField && municipalityField.value) {
                ids.push({ id: municipalityField.value, lookup: lookups.municipalities, zoom: 12 });
            }
            if (provinceField && provinceField.value) {
                ids.push({ id: provinceField.value, lookup: lookups.provinces, zoom: 9 });
            }
            if (regionField && regionField.value) {
                ids.push({ id: regionField.value, lookup: lookups.regions, zoom: 7 });
            }
            var best = findBestCoordinates(lookups, ids);
            if (best) {
                map.setView([best.lat, best.lng], best.zoom);
            }
        }

        if (selectionField) {
            selectionField.addEventListener("change", renderSelectedCommunities);
        }

        [regionField, provinceField, municipalityField, barangayField]
            .filter(Boolean)
            .forEach(function (field) {
                field.addEventListener("change", function () {
                    if (markerLayer.getLayers().length === 0) {
                        recenterFromCoverage();
                    }
                });
            });

        recenterFromCoverage();
        renderSelectedCommunities();
    }

    function setupCoverageMap(container, externalConfig) {
        var mapNode = container.querySelector("[data-obc-map-target]");
        if (!mapNode) {
            return;
        }

        var dataset = container.dataset || {};
        var map = createMap(mapNode, dataset);
        var markerLayer = window.L.layerGroup().addTo(map);

        var locationData = parseJsonScript(dataset.locationScript);
        var lookups = {
            regions: buildLookup(locationData && locationData.regions),
            provinces: buildLookup(locationData && locationData.provinces),
            municipalities: buildLookup(locationData && locationData.municipalities),
            barangays: buildLookup(locationData && locationData.barangays),
        };

        var selectors = externalConfig || {};
        var regionField = resolveElement(selectors.regionSelect) || resolveElement(dataset.regionField);
        var provinceField = resolveElement(selectors.provinceSelect) || resolveElement(dataset.provinceField);
        var municipalityField = resolveElement(selectors.municipalitySelect) || resolveElement(dataset.municipalityField);
        var barangayField = resolveElement(selectors.barangaySelect) || resolveElement(dataset.barangayField);

        var centroidUrl = selectors.centroidUrl || dataset.centroidUrl || "";
        var fetchCentroid = createCentroidFetcher(centroidUrl);
        var centroidRequestId = 0;

        function currentSelectionHierarchy() {
            return [
                {
                    field: barangayField,
                    level: "barangay",
                    lookup: lookups.barangays,
                    zoom: 15,
                },
                {
                    field: municipalityField,
                    level: "municipality",
                    lookup: lookups.municipalities,
                    zoom: 12,
                },
                {
                    field: provinceField,
                    level: "province",
                    lookup: lookups.provinces,
                    zoom: 9,
                },
                {
                    field: regionField,
                    level: "region",
                    lookup: lookups.regions,
                    zoom: 7,
                },
            ];
        }

        function drawMarker(lat, lng, zoom) {
            if (lat === null || lng === null) {
                return;
            }
            markerLayer.clearLayers();
            window.L.marker([lat, lng]).addTo(markerLayer);
            if (zoom !== null && zoom !== undefined) {
                map.setView([lat, lng], zoom);
            } else {
                map.setView([lat, lng]);
            }
        }

        function computeFetchTarget(selectionHierarchy) {
            for (var i = 0; i < selectionHierarchy.length; i += 1) {
                var entry = selectionHierarchy[i];
                if (entry.field && entry.field.value) {
                    return {
                        level: entry.level,
                        id: entry.field.value,
                        zoom: entry.zoom,
                    };
                }
            }
            return null;
        }

        function determineLocalBest(selectionHierarchy) {
            var ids = selectionHierarchy.map(function (entry) {
                return {
                    id: entry.field && entry.field.value ? entry.field.value : null,
                    lookup: entry.lookup,
                    zoom: entry.zoom,
                };
            });
            return findBestCoordinates(lookups, ids);
        }

        function recenter() {
            var hierarchy = currentSelectionHierarchy();
            var best = determineLocalBest(hierarchy);
            var fetchTarget = computeFetchTarget(hierarchy);

            if (best) {
                drawMarker(best.lat, best.lng, best.zoom);
            } else {
                markerLayer.clearLayers();
            }

            if (!fetchTarget) {
                return;
            }

            centroidRequestId += 1;
            var requestToken = centroidRequestId;
            fetchCentroid(fetchTarget.level, fetchTarget.id).then(function (payload) {
                if (requestToken !== centroidRequestId) {
                    return;
                }
                if (!payload || !payload.has_location) {
                    return;
                }
                drawMarker(payload.lat, payload.lng, fetchTarget.zoom);
            });
        }

        [regionField, provinceField, municipalityField, barangayField]
            .filter(function (field) {
                return !!field;
            })
            .forEach(function (field) {
                field.addEventListener("change", recenter);
            });

        container.__obcCoverageRefresh = recenter;
        recenter();
    }

    function initContainer(container, externalConfig) {
        if (!container || isInitialised(container)) {
            return;
        }
        if (typeof window.L === "undefined") {
            console.warn("Leaflet library not loaded; skipping OBC map initialisation.");
            return;
        }
        var mode = container.dataset.mode || "detail";
        if (mode === "form") {
            setupFormMap(container);
        } else if (mode === "multi") {
            setupMultiMap(container);
        } else if (mode === "coverage") {
            setupCoverageMap(container, externalConfig || {});
        } else {
            setupDetailMap(container);
        }
        markInitialised(container);
    }

    function initialiseAll() {
        if (typeof window.L === "undefined") {
            console.warn("Leaflet library not loaded; skipping OBC map initialisation.");
            return;
        }
        var containers = document.querySelectorAll("[data-obc-map]");
        containers.forEach(function (container) {
            initContainer(container);
        });
    }

    window.OBCMaps = {
        initContainer: initContainer,
        initCoverageMap: function (container, config) {
            if (!container) {
                return;
            }
            if (!container.dataset.mode) {
                container.dataset.mode = "coverage";
            }
            initContainer(container, config || {});
        },
        refreshCoverage: function (container) {
            if (container && typeof container.__obcCoverageRefresh === "function") {
                container.__obcCoverageRefresh();
            }
        },
    };

    document.addEventListener("DOMContentLoaded", initialiseAll);
})();

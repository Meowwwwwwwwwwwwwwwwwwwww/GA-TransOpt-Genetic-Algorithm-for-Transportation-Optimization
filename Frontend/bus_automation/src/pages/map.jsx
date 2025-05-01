import { useState, useEffect } from "react";
import axios from "axios";

export default function RouteMap() {
  const [routes, setRoutes] = useState([]);
  const [stopMap, setStopMap] = useState({});
  const [loading, setLoading] = useState(true);  // Add loading state

  useEffect(() => {
    axios.get('http://localhost:5000/api/optimized-routes') // adjust if needed
      .then((res) => {
        const { busroutes, stops } = res.data;

        const stopLookup = {};
        stops.forEach(s => {
          stopLookup[s.id] = s.coordinates;
        });

        setStopMap(stopLookup);

        const routeLines = Object.entries(busroutes).map(([busId, stopIds]) => ({
          busId,
          path: stopIds.map(id => stopLookup[id]),
        }));

        setRoutes(routeLines);
        setLoading(false);  // Set loading to false once data is fetched
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setLoading(false);  // Set loading to false in case of an error
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;  // Display a loading message
  }

  return (
    <MapContainer center={[37.7749, -122.4194]} zoom={10} style={{ height: '100vh', width: '100%' }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {routes.map((route, index) => (
        <Polyline key={index} positions={route.path} color={colors[index % colors.length]} />
      ))}
      {Object.entries(stopMap).map(([stopId, coordinates]) => (
        <Marker key={stopId} position={coordinates}>
          <Popup>{stopId}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

import numpy as np
from scipy.interpolate import interp2d


def interpolate_discrete(lat, long, grid_array, array_latitudes, array_longitudes, sector_interpolation=False,
                         step=0.01):
    """Given K 2D-arrays, representing some K-dim magnitude values, interpolates the K values for a given latitude and
    longitude. It can also return the interpolated values for the sector the lat, long pint yields on.

    Params:
    ------

    lat: float. Latitude. long: float. Longitude. grid_array: array. An (M, N, K)-dimensional array containing the
    K-dim values of the magnitude. Each MxN matrix element represents the value for the k_th dimension of that
    magnitude in the m_th, n_th latitude, longitude point on the discrete space. array_latitudes: array. An (
    M)-dimensional vector with the latitude values corresponding to the discrete points of the grid_array.
    array_longitudes: array. An (N)-dimensional vector with the longitude values corresponding to the discrete points
    of the grid_array. sector_interpolation: boolean. Default = False. Whether to interpolate the sector or not.
    step: float. Default = 0.01. If interpolating the sector, the step of the new discrete map.


    Returns:
    ------
    interpolated_values: array. (K)-dimensional vector with the interpolated values.
    lat_s, long_s: arrays. [ONLY IF sector_interpolation = True] (M')-dim and (N')-dim arrays containing the lats and
        longs of the interpolated sector
    interpolated_sector. [ONLY IF sector_interpolation = True] (M', N', K)-dim array containing the interpolated values
        for the whole sector

    """

    # Look for the closest grid points
    idx = (np.abs(array_latitudes - lat)).argmin()
    idy = (np.abs(array_longitudes - long)).argmin()

    # Check if the closest grid point is "above" or "bellow"
    if array_latitudes[0][idx] < lat:
        idx += 1
    if array_longitudes[1][idy] < long:
        idy += 1

    # Select the sector to interpolate
    small_lat = array_latitudes[idx:idx + 2]
    small_long = array_longitudes[idy:idy + 2]
    small_array = grid_array[idx:idx + 2, idy:idy + 2, :]

    k_dimensions = small_array.shape[2]

    # Interpolation for each matrix
    interpolated_values = np.empty([k_dimensions])
    if sector_interpolation:
        lat_s = np.arange(array_latitudes[idx], array_latitudes[idx + 1], step)
        long_s = np.arange(array_longitudes[idx], array_longitudes[1][idx + 1], step)
        interpolated_sector = np.empty([len(lat_s), len(long_s), k_dimensions])
    for dimension in np.arange(k_dimensions):
        interpolation_function = interp2d(small_lat, small_long, small_array[:, :, dimension])

        # Interpolate value
        np.append(interpolated_values, interpolation_function(lat, long))

        if sector_interpolation:
            np.append(interpolated_sector, interpolation_function(lat_s, long_s), axis=2)

    if sector_interpolation:
        return interpolated_values, lat_s, long_s, interpolated_sector
    else:
        return interpolated_values


def velocity_composition(boat_velocity, lat, long, stream_velocities, stream_velocities_latitudes, stream_velocities_longitudes):
    """Given streams velocities on a discrete grid of latitude and longitude points, and a determined boat velocity, it
    compounds the sum of both velocities, interpolating the stream velocity for the latitude and longitude
    position of the boat.

    Params:
    ------

    boat_velocity: array. Vector containing the latitude and longitude components of the boat velocity, in that order.
    lat: float. Latitude.
    long: float. Longitude.
    grid_array: array. An (M, N, K)-dimensional array containing the K-dim values of the magnitude. Each MxN matrix
        element represents the value for the k_th dimension of that magnitude in the m_th, n_th latitude, longitude point
        on the discrete space.
    array_latitudes: array. An (M)-dimensional vector with the latitude values corresponding to the discrete points of
        the grid_array.
    array_longitudes: array. An (N)-dimensional vector with the longitude values corresponding to the discrete points of
        the grid_array.

    Returns:
    ------

    velocity. array. A vector with the composed sum of velocities, with the latitude and longitude components on that
        order.
"""
    interpolated_stream_velocities = interpolate_discrete(lat, long, stream_velocities, stream_velocities_latitudes, stream_velocities_longitudes)
    velocity = boat_velocity + interpolated_stream_velocities

    return velocity


def boat_movement(boat_velocity, lat, long, stream_velocities, stream_velocities_latitudes, stream_velocities_longitudes, ts):
    """Computes the new position of the boat given the boat velocity, the steams velocity and the timestamp. Timestamp
    is assumed to be so small that the stream velocity does not change from the initial point to the final one.

    Params:
    ------

    boat_velocity: array. Vector containing the latitude and longitude components of the boat velocity, in that order.
    lat: float. Latitude.
    long: float. Longitude.
    grid_array: array. An (M, N, K)-dimensional array containing the K-dim values of the magnitude. Each MxN matrix
        element represents the value for the k_th dimension of that magnitude in the m_th, n_th latitude, longitude point
        on the discrete space.
    array_latitudes: array. An (M)-dimensional vector with the latitude values corresponding to the discrete points of
        the grid_array.
    array_longitudes: array. An (N)-dimensional vector with the longitude values corresponding to the discrete points of
        the grid_array.
    ts: float. The time increment interval [THIS VALUE IS ASSUMED TO BE SMALL SO THE DISPLACEMENT IS SHORT].

    Returns:
    ------

    new_latitude, new_longitude. floats. The values for the latitude and longitude new positions.

    """

    velocity = velocity_composition(boat_velocity, lat, long, stream_velocities, stream_velocities_latitudes, stream_velocities_longitudes)
    new_latitude = lat + velocity[0] * ts
    new_longitude = lat + velocity[1] * ts
    return new_latitude, new_longitude

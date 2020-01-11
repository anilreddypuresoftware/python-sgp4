"""The Satellite class."""

from sgp4.earth_gravity import wgs72
from sgp4.ext import jday
from sgp4.propagation import sgp4

minutes_per_day = 1440.

# TODO: have this be a subclass of a plainer Satrec class.
# TODO: add a SatrecArray to this file too?
# TODO: okay, complicated: need to import twoline2rv but drat it imports us;
#  so, switch things around so it expects blank object to be passed it;
#  have legacy old function in io.py that on-the-fly imports and builds old compat model.
#  Hmm. Really? That will make things more expensive for all old users,
#  is there an alternative?

from sgp4.io import twoline2rv

class Satrec(object):
    @classmethod
    def twoline2rv(cls, line1, line2):
        self = cls()
        twoline2rv(line1, line2, wgs72, 'i', self)
        return self

    def sgp4(self, jd, fr):
        tsince = (jd - self.jdsatepoch + fr) * minutes_per_day
        r, v = sgp4(self, tsince)
        return self.error, r, v

class SatrecArray(object):
    def __init__(self, satrecs):
        self._satrecs = satrecs
        # Cache optional import that we now know we need.
        from numpy import array
        self.array = array

    def sgp4(self, jd, fr):
        result = []
        for satrec in self._satrecs:
            result.append(satrec.sgp4(jd, fr))
        return self.array(result).T #self.error, r, v

class Satellite(object):
    """The old Satellite object for compatibility with sgp4 1.x.

    Most of this class's hundred-plus attributes are intermediate values
    of interest only to the propagation algorithm itself.  Here are the
    attributes set by ``sgp4.io.twoline2rv()`` in which users are likely
    to be interested:

    ``satnum``
        Unique satellite number given in the TLE file.
    ``epochyr``
        Full four-digit year of this element set's epoch moment.
    ``epochdays``
        Fractional days into the year of the epoch moment.
    ``jdsatepoch``
        Julian date of the epoch (computed from ``epochyr`` and ``epochdays``).
    ``ndot``
        First time derivative of the mean motion (ignored by SGP4).
    ``nddot``
        Second time derivative of the mean motion (ignored by SGP4).
    ``bstar``
        Ballistic drag coefficient B* in inverse earth radii.
    ``inclo``
        Inclination in radians.
    ``nodeo``
        Right ascension of ascending node in radians.
    ``ecco``
        Eccentricity.
    ``argpo``
        Argument of perigee in radians.
    ``mo``
        Mean anomaly in radians.
    ``no_kozai``
        Mean motion in radians per minute.

    """
    # TODO: only offer this on legacy class we no longer document
    def propagate(self, year, month=1, day=1, hour=0, minute=0, second=0.0):
        """Return a position and velocity vector for a given date and time."""

        j = jday(year, month, day, hour, minute, second)
        m = (j - self.jdsatepoch) * minutes_per_day
        r, v = sgp4(self, m)
        return r, v

    @property
    def no(self):
        """Support renamed attribute for any code still using the old name."""
        return self.no_kozai

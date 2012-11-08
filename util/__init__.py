import datetime
from verlib import suggest_normalized_version, NormalizedVersion
import warnings

getCurrentDateTime = datetime.datetime.now
getCurrentDateTimeString = lambda : getCurrentDateTime().strftime("%Y-%m-%d %H:%M")


def validate_version(version):
    rversion = suggest_normalized_version(version)
    if rversion is None:
        raise ValueError('Cannot work with "%s"' % version)
    if rversion != version:
        warnings.warn('"%s" is not a normalized version.\n'
                      'It has been transformed into "%s" '
                      'for interoperability.' % (version, rversion))
    return NormalizedVersion(rversion)


#  331     public boolean contains(double x, double y) {
#  332         // Normalize the coordinates compared to the ellipse
#  333         // having a center at 0,0 and a radius of 0.5.
#  334         double ellw = getWidth();
#  335         if (ellw <= 0.0) {
#  336             return false;
#  337         }
#  338         double normx = (x - getX()) / ellw - 0.5;
#  339         double ellh = getHeight();
#  340         if (ellh <= 0.0) {
#  341             return false;
#  342         }
#  343         double normy = (y - getY()) / ellh - 0.5;
#  344         return (normx * normx + normy * normy) < 0.25;
#  345     }

try:
    import describeModule
except:
    pass

try:
    import systemInfo
except:
    pass

import datetime

try:
    from verlib import suggest_normalized_version, NormalizedVersion

    def validate_version(version):
        rversion = suggest_normalized_version(version)
        if rversion is None:
            raise ValueError('Cannot work with "%s"' % version)
        if rversion != version:
            warnings.warn('"%s" is not a normalized version.\n'
                          'It has been transformed into "%s" '
                          'for interoperability.' % (version, rversion))
        return NormalizedVersion(rversion)

except:
    # just use the version provided if verlib is not installed.
    validate_version=lambda version: version

import warnings

getCurrentDateTime = datetime.datetime.now
getCurrentDateTimeString = lambda : getCurrentDateTime().strftime("%Y-%m-%d %H:%M")

try:
    import experiment
except:
    pass

try:
    import describeModule
except:
    pass

try:
    import systemInfo
except:
    pass

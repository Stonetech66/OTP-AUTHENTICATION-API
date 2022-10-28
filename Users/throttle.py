from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class StrictUSerThrottle(UserRateThrottle):
    scope='strict-user'
    rate='4/minute'

class StrictAnonThrottle(AnonRateThrottle):
    scope='strict-anon'
    rate='4/minute'



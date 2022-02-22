#!/usr/bin/python3

# Author: John Khoo (john_khoo@u.nus.edu)

from autotele import Autotele, time_to_epoch, TOL_SECS
import sys
import datetime as dtime

MASS_BOOKING = """
Dear brothers and sisters, booking for Mass begins today at https://mycatholic.sg\n\nChurches with Mass Booking Time starting at 9am\n- Church of the Holy Trinity\n- Church of St Michael\n- St Mary of the Angels\n- Church of the Holy Spirit\n- Church of St Stephen\n- Church of Sts Peter and Paul\n- St Anne's Church\n- Church of St Alphonsus (Novena)\n- Church of Our Lady of Perpetual Succour\n- St Joseph Church (Victoria Street)\n- Cathedral of the Good Shepherd\n \nChurches with Mass Booking Time starting at 12pm\n- Church of Our Lady of Lourdes\n- Church of Christ the King\n- Immaculate Heart of Mary\n- Church of Divine Mercy\n- Church of St Bernadette\n- Church of St Francis of Assisi\n- St Joseph's Church (Bukit Timah)\n- Church of St Francis Xavier\n- Church of the Risen Christ\n- Blessed Sacrament Church\n- Church of St Vincent de Paul\n\nChurches with Mass Booking Time starting at 3pm\n- Church of Our Lady Queen of Peace\n- Church of the Holy Cross\n- Church of Our Lady Star of the Sea (OLSS)\n- Church of St Anthony\n- Church of St Ignatius\n- Church of the Holy Family\n- Church of the Sacred Heart\n- Church of the Transfiguration\n- Church of the Nativity of the Blessed Virgin Mary\n- Church of St Teresa\n\nJesus waits for each one of us in the tabernacle. Let's take each opportunity we can get to receive Our Blessed Lord!
"""
MASS_BOOKING_ENTITIES = [
            {
                "@type": "textEntity",
                "offset": 60,
                "length": 21,
                "type": {"@type": "textEntityTypeUrl"}
            },
            {   
                "@type": "textEntity",
                "offset": 83,
                "length": 48,
                "type": {"@type": "textEntityTypeUnderline"}
            },
            {
                "@type": "textEntity",
                "offset": 456,
                "length": 49,
                "type": {"@type": "textEntityTypeUnderline"}
            },
            {
                "@type": "textEntity",
                "offset": 829,
                "length": 48,
                "type": {"@type": "textEntityTypeUnderline"}
            }
        ]
MASS_BOOKING_WEEKDAY = 1  # Tuesday
MASS_BOOKING_HOUR = 9
MASS_BOOKING_MIN = 0

AT = Autotele(sys.argv)
AT.authenticate()

# find first Tuesday in month
if AT.custom_date is None:
    sgtz = dtime.timezone(dtime.timedelta(hours=8))  # ensure timezone is correct
    dt = dtime.datetime.now(sgtz)
else:
    dt = AT.custom_date
target_date = dtime.datetime(dt.year, dt.month, 1, MASS_BOOKING_HOUR, MASS_BOOKING_MIN)
while target_date.weekday() != MASS_BOOKING_WEEKDAY:
    target_date += dtime.timedelta(days=1)

# find all Tuesdays
curr_date = target_date
sched_dts = []
while curr_date.month == target_date.month:
    sched_dts.append(curr_date)
    curr_date += dtime.timedelta(weeks=1)

pending_scheds = {
    int(dt.timestamp()): (MASS_BOOKING, MASS_BOOKING_ENTITIES) for dt in sched_dts
}
AT.schedule(pending_scheds, AT.secrets['legion_channel'])

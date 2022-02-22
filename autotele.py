#!/usr/bin/python3

# Author: John Khoo (john_khoo@u.nus.edu)

from autotele import Autotele, time_to_epoch, TOL_SECS
import sys
import datetime as dtime

ANGELUS = """
The Angel of the Lord declared to Mary: And she conceived of the Holy Spirit. Hail Mary...

Behold the handmaid of the Lord: Be it done unto me according to Thy word. Hail Mary...

And the Word was made Flesh:
And dwelt among us. Hail Mary...

Pray for us, O Holy Mother of God, that we may be made worthy of the promises of Christ. 

Let us pray:

Pour forth, we beseech Thee, O Lord, Thy grace into our hearts; that we, to whom the incarnation of Christ, Thy Son, was made known by the message of an angel, may by His Passion and Cross be brought to the glory of His Resurrection, through the same Christ Our Lord. Amen.
"""

EXAMEN = """
As the day draws to a close, let us take a few minutes to examine our day in God's presence. Begin by acknowledging the presence of God, giving thanks for the day that has passed, and asking for His light as you review it. Then, step through the events of the day, from when you woke up, praising God with gratitude for the blessings you have received and humbly asking His forgiveness for the times you have failed Him. Here are some questions to help in our reflection!

- Do I love God? Do I prioritise and seek to glorify Him, to worship Him as He deserves, and to understand and follow His commandments?
- Am I constantly aware of the presence of God in everything I do, and His love for me? Do I draw peace and joy from the knowledge that I am His child, or do I allow worldly cares to overwhelm me? Do I trust in God's love?
- Did things go according to plan today, or even better than expected? Have I been grateful for these occasions?
- Did anyone go out of his way today to help me? Did I acknowledge him with gratitude?
- Did I have any unpleasant interactions with people today? Why were they unpleasant?
- Have I fulfilled my responsibilities to my family, friends, and work? Do I love my family and friends? Do they know that I love them?
- Have I wasted my time today, or caused other people to waste their time? Have I used my resources (talents, money, belongings, etc.) well?
- Do I bear the difficulties of each day with patience, in union with Christ? Am I overly attached to comfort, preference, and convenience?
- Have I entertained prideful, lustful, hateful, envious, etc. thoughts instead of resisting them?
- Have I been dishonest? Have I discussed the faults of others unnecessarily?
- Do I humbly acknowledge my faults and ask forgiveness from people? Do I forgive others? Do I seek to grow from my mistakes, and help others to grow too?
- Have I taken reasonable care of my health?
- Have I tried to bring the love of Christ to others today, and to lead them to Him?

No matter how well or badly your day has gone, God loves you with an eternal love. If we open our hearts to Him, He will give us the grace to do better. Even the gravest of sins can be forgiven, and our relationship with God restored, in Confession. Let's keep praying for each other!
"""

AT = Autotele(sys.argv)
# compute unix timestamps to send messages tomorrow
if AT.custom_date is None:
    sgtz = dtime.timezone(dtime.timedelta(hours=8))  # ensure timezone is correct
    target_date = dtime.datetime.now(sgtz) + dtime.timedelta(days=1)
else:
    target_date = AT.custom_date

morning_angelus = int(time_to_epoch(target_date, 6, 0))
noon_angelus = int(time_to_epoch(target_date, 12, 0))
evening_angelus = int(time_to_epoch(target_date, 18, 0))
examen = int(time_to_epoch(target_date, 22, 30))
pending_scheds = {
    morning_angelus: ANGELUS,
    noon_angelus: ANGELUS,
    evening_angelus: ANGELUS,
    examen: EXAMEN,
}
AT.schedule(pending_scheds, AT.secrets['angelus_channel'])

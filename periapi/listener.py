#!/usr/bin/env python3
"""
Periscope API for the masses
"""

from dateutil.parser import parse as dt_parse

from periapi.broadcast import Broadcast


class Listener:
    """Class to check notifications stream for new broadcasts and return new broadcast ids"""

    def __init__(self, api, check_backlog=False, cap_invited=False):
        print("Check backlog is: " + str(check_backlog))
        print("Cap Invited is: " + str(cap_invited))
        self.api = api

        self.follows = set([i['username'] for i in self.api.following])
        self.config = self.api.session.config

        self.check_backlog = check_backlog
        self.cap_invited = cap_invited

    def check_for_new(self):
        """Check for new broadcasts"""
        current_notifications = self.api.notifications

        if len(current_notifications) == 0:
            return None

        new_broadcasts = self.process_notifications(current_notifications)

        if len(new_broadcasts) == 0:
            return None

        return new_broadcasts

    def process_notifications(self, notifications):
        """Process list of broadcasts obtained from notifications API endpoint."""
        new_broadcasts = list()
        new = self.new_follows()

        for i in notifications:

            broadcast = Broadcast(self.api, i)

            if self.check_if_wanted(broadcast, new):
                new_broadcasts.append(broadcast)

        if self.check_backlog:
            self.check_backlog = False

        return new_broadcasts

    def check_if_wanted(self, broadcast, new):
        """Check if broadcast in notifications string is desired for download"""
        if self.check_backlog:
            return True

        if not self.cap_invited:
            if broadcast.username in self.follows:
                return True

        elif new:
            if broadcast.username in new:
                return True

        elif self.last_new_bc:
            if broadcast.start_dt > dt_parse(self.last_new_bc):
                return True

        return None

    def new_follows(self):
        """Get set of new follows since last check"""
        cur_follows = set([i['username'] for i in self.api.following])
        new_follows = cur_follows - self.follows
        self.follows = cur_follows
        if len(new_follows) > 0:
            return new_follows
        return None

    @property
    def last_new_bc(self):
        """Get the ATOM timestamp of when the last new broadcast was found."""
        return self.config.get('last_check')

    @last_new_bc.setter
    def last_new_bc(self, when):
        """Set the ATOM timestamp of when the last new broadcast was found."""
        self.config['last_check'] = when
        self.config.write()
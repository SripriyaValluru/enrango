#
# models.py
#
# Copyright 2013 Thomas Sigurdsen <thomas.sigurdsen@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import ModelForm


class Event(models.Model):
    """The events the app is managing enrolled users for.

    TODO: Meta subclass?
    """
    title = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_event = models.DateTimeField(auto_now_add=False)
    max_participants = models.PositiveIntegerField()

    def __unicode__(self):
        return self.title

    def get_empty_seats(self):
        """Returns number (possibly negative) of free seats for this event"""
        pc = int(Participant.objects.filter(event__exact=self.id).count())
        return self.max_participants - pc
    get_empty_seats.admin_order_field = 'max_participants'
    get_empty_seats.short_description = 'Number of free seats'

    @models.permalink
    def get_absolute_url(self):
        return ('enrango.views.event', [str(self.id)])


class Participant(models.Model):
    """
    Participants are currently required to leave this info. Should be fixed.

    Rationale: event producer needs to send bills using this info. By fixing I
    mean make it customizable, preferrably via the admin interface. TODO

    TODO: Meta subclass?
    """
    name = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    phone = models.PositiveIntegerField()
    email = models.EmailField()
    address = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH)
    identifier = models.PositiveIntegerField(max_length=settings.MAX_CHARFIELD_LENGTH)
    STATUSENUM = (
        (u'NA', u'Not Available'),
        (u'EN', u'Enrolled'),
        (u'WA', u'Waiting in queue'),
    )
    status = models.CharField(max_length=settings.MAX_CHARFIELD_LENGTH,
                              choices=STATUSENUM,
                              default=u'NA')
    event = models.ForeignKey(Event)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.identifier = abs(hash(self.name + str(self.phone)))
        super(Participant, self).save(*args, **kwargs)

    def check_phonenumber_length(self):
        """Norwegian phonenumbers are between 8 and 12 digits long

        Returns true if length is ok.
        TODO: do a more thorough/robust check.
        """
        if len(str(abs(self))) is not 8:
            raise ValidationError(u'%s does not look like a phonenumber \
                                  (Standard Norwegian phonenumbers are 8 \
                                  digits long).' % self)
        return True

    phone.validators = [check_phonenumber_length]


class ParticipantForm(ModelForm):
    class Meta:
        model = Participant
        exclude = ('identifier', 'status', 'event',)

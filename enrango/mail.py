#
# mail.py
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
import smtplib
from django.conf import settings
from django.shortcuts import render_to_response
from enrango.utility import get_possessive, get_participant_url


def send_enrollment(participant):
    # TODO: check for success
    fromaddr = settings.ENRANGO_EMAIL
    toaddr = participant.email
    message = (u'From: %s\r\nTo: %s\r\n' % (fromaddr, toaddr))
    message = (message + u'Subject: Activation required for enrollment\r\n')
    message = (message +
               str(render_to_response('enrango/enroll_mail.html', {
                   'participant': participant,
                   'participant_url': get_participant_url(participant),
                   'participant_possessive': get_possessive(participant),
               },)))
    smtpserver = smtplib.SMTP_SSL(host=settings.EMAIL_HOST,
                                  port=settings.EMAIL_PORT)
    if settings.EMAIL_USE_TLS:
        smtpserver.login(user=settings.EMAIL_HOST_USER,
                         password=settings.EMAIL_HOST_PASSWORD)

    smtpserver.set_debuglevel(0)
    return smtpserver.sendmail(fromaddr, toaddr, message)

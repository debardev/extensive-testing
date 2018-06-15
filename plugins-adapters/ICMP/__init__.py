#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
# This file is part of the extensive automation project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

try:
	from sniffer import *
	from codec4 import *
	from ping import *
except ImportError: # python3 support
	from .sniffer import *
	from .codec4 import *
	from .ping import *
	
__DESCRIPTION__ = """This adapter enables to send/receive ICMP packet (request/reply or other).

Internet Control Message Protocol (ICMP) messages are typically used for diagnostic or control.

More informations in the RFC792, RFC1122, RFC950."""
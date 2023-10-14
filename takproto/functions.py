#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2023 Sensors & Signals LLC
# Copyright 2020 Delta Bravo-15 <deltabravo15ga@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""TAKProto Functions for manipulating TAK Protocol Version 1 messages."""

import re
import xml.etree.ElementTree as ET

from datetime import datetime
from io import BytesIO
from typing import Optional

import delimited_protobuf as dpb

from takproto.constants import (
    ISO_8601_UTC,
    DEFAULT_MESH_HEADER,
    DEFAULT_PROTO_HEADER,
    TAKProtoVer,
)
from takproto.proto import TakMessage


def parse_proto(msg: bytearray) -> Optional[bytearray]:
    """Parse TAK Protocol Version 1 Mesh & Stream message."""
    parsed = None

    if msg[:3] == DEFAULT_MESH_HEADER:
        parsed = parse_mesh(msg)
    elif msg[0] in DEFAULT_PROTO_HEADER:
        parsed = parse_stream(msg)
    return parsed


def parse_mesh(msg):
    """Parse TAK Protocol Version 1 Mesh message."""
    msg = msg[3:]
    protobuf = TakMessage()
    protobuf.ParseFromString(bytes(msg))
    return protobuf


def parse_stream(msg):
    """Parse TAK Protocol Version 1 Stream message."""
    bio = BytesIO(msg[1:])
    msg = dpb.read(bio, TakMessage)
    return msg


def format_time(time: str) -> int:
    """Format timestamp as microseconds."""
    s_time = datetime.strptime(time + "+0000", ISO_8601_UTC + "%z")
    return int(s_time.timestamp() * 1000)


def xml2proto(
    xml: str, protover: Optional[TAKProtoVer] = None
):  # NOQA pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Convert plain XML CoT to Protobuf."""
    event = ET.fromstring(xml)
    tak_message = TakMessage()
    tak_control = tak_message.takControl
    new_event = tak_message.cotEvent

    # If this is a GeoChat message, extract the sender's UID from the event UID and
    # place it in takControl.contactUid
    uid = event.get("uid")
    if uid and "GeoChat." in uid:
        tak_control.contactUid = uid.split(".")[1]

    base_attribs = ["type", "access", "qos", "opex", "uid", "how"]
    for attrib in base_attribs:
        val = event.get(attrib)
        if val:
            setattr(new_event, attrib, val)

    # TAK protobuf times are expressed as miliseconds since 1970-01-01 00:00:00 UTC
    # Convert time, start, and stale, from ISO time format to miliseconds since epoch
    time_attribs = ["time", "start", "stale"]
    for attrib in time_attribs:
        val = event.get(attrib)
        if val:
            if attrib == "time":
                attrib = "send"
            setattr(new_event, f"{attrib}Time", format_time(val))

    # If the event element includes a point child, write the attributes
    point = event.find("point")
    if point is not None:
        attribs = ["lat", "lon", "hae", "ce", "le"]
        for attrib in attribs:
            val = point.get(attrib)
            if val:
                setattr(new_event, attrib, float(val))

    detail = event.find("detail")
    if detail is not None:
        # If the XML includes a <detail> element, create new_event.detail
        new_detail = new_event.detail

        # The new_event.detail field of a TAK protobuf is structured differently
        # from CoT XML. new_event.detail may only contain xmlDetail, contact,
        # __group, precisionlocation, status, takv, and track. xmlDetail should
        # contain an XML string with any data that does not adhere to the other
        # strongly-typed fields. See more information about each field below.

        # If this is a GeoChat message, write the contents of <detail> in xmlDetail.
        if uid and "GeoChat." in uid:
            pattern = "<detail>(.*?)</detail>"
            xmldetailstr = re.search(pattern, xml).group(1)
            new_detail.xmlDetail = xmldetailstr
        else:
            # Add unknown elements to xmlDetail field.
            known_elem = [
                "contact",
                "__group",
                "precisionlocation",
                "status",
                "takv",
                "track",
            ]
            for elem in detail.iterfind("*"):
                if elem.tag not in known_elem:
                    new_detail.xmlDetail = ET.tostring(elem).strip()

        contact = detail.find("contact")
        if contact is not None:
            attribs = ["endpoint", "callsign"]
            for attrib in attribs:
                attrib_val = contact.get(attrib)
                if attrib_val:
                    setattr(new_detail.contact, attrib, attrib_val)

        group = detail.find("__group")  # pylint: disable=protected-access
        if group is not None:
            attribs = ["name", "role"]
            for attrib in attribs:
                attrib_val = group.get(attrib)
                if attrib_val:
                    setattr(new_detail.group, attrib, attrib_val)

        prec_loc = detail.find("precisionlocation")
        if prec_loc is not None:
            attribs = ["geopointsrc", "altsrc"]
            for attrib in attribs:
                attrib_val = prec_loc.get(attrib)
                if attrib_val:
                    setattr(new_detail.precisionLocation, attrib, attrib_val)

        status = detail.find("status")
        if status is not None:
            battery = status.get("battery")
            if battery:
                new_detail.status.battery = int(battery)

        takv = detail.find("takv")
        if takv is not None:
            attribs = ["device", "platform", "os", "version"]
            for attrib in attribs:
                attrib_val = takv.get(attrib)
                if attrib_val:
                    setattr(new_detail.takv, attrib, attrib_val)

        # The fields in track are double-precision floating-point numbers.
        # We can use Python's native float, since that is actually 64-bit
        # floating-point.
        track = detail.find("track")
        if track is not None:
            attribs = ["speed", "course"]
            for attrib in attribs:
                attrib_val = track.get(attrib)
                if attrib_val:
                    setattr(new_detail.track, attrib, float(attrib_val))

    output = msg2proto(tak_message, protover)
    return output


def msg2proto(msg, protover: Optional[TAKProtoVer] = None) -> bytearray:
    """Convert a TakMessage into a TAK Protocol Version 1 protobuf."""
    protover = protover or TAKProtoVer.MESH

    output_ba = bytearray()
    header_ba = bytearray()
    proto_ba = bytearray()

    if protover == TAKProtoVer.MESH:
        header_ba = DEFAULT_MESH_HEADER
        proto_ba = bytearray(msg.SerializeToString())
    elif protover == TAKProtoVer.STREAM:
        header_ba = DEFAULT_PROTO_HEADER
        output_io = BytesIO()
        dpb.write(output_io, msg)
        proto_ba = bytearray(output_io.getvalue())
    else:
        raise ValueError(f"Unsupported TAKProtoVer: {protover}")

    output_ba = header_ba + proto_ba
    return output_ba

def unformat_time(i_time: int) -> str:
    s = datetime.utcfromtimestamp(i_time/1000)
    return s.isoformat()[:-3] + "Z"


def msg2xml(msg) -> bytes:
    # print(msg)
    if hasattr(msg, "cotEvent"):
        e = msg.cotEvent
    else:
        e = msg
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", e.type)
    if "access" in [desc.name for desc, val in e.ListFields()]:
        root.set("access", e.access)
    if "qos" in [desc.name for desc, val in e.ListFields()]:
        root.set("qos", e.qos)
    if "opex" in [desc.name for desc, val in e.ListFields()]:
        root.set("opex", e.opex)
    root.set("uid", e.uid)
    root.set("how", e.how)
    root.set("time", unformat_time(e.sendTime))
    root.set("start", unformat_time(e.startTime))
    root.set("stale", unformat_time(e.staleTime))
    point = ET.SubElement(root, "point")
    point.set("lat", str(e.lat))
    point.set("lon", str(e.lon))
    point.set("hae", str(e.hae))
    point.set("ce", str(e.ce))
    point.set("le", str(e.le))
    # print(ET.tostring(root))
    if "detail" in [desc.name for desc, val in e.ListFields()]:
        detail = ET.SubElement(root, "detail")
        # print(e.detail.xmlDetail)
        if "xmlDetail" in [desc.name for desc, val in e.detail.ListFields()]:
            xml_detail = ET.fromstring('<xml_detail>' + e.detail.xmlDetail + '</xml_detail>')
            # print(ET.tostring(xml_detail))
            for detail_element in xml_detail:
                detail.append(detail_element)
            # print(ET.tostring(root))
        if "contact" in [desc.name for desc, val in e.detail.ListFields()]:
            contact = ET.SubElement(detail, "contact")
            if "endpoint" in [desc.name for desc, val in e.detail.contact.ListFields()]:
                contact.set("endpoint", e.detail.contact.endpoint)
            if "callsign" in [desc.name for desc, val in e.detail.contact.ListFields()]:
                contact.set("callsign", e.detail.contact.callsign)
        if "group" in [desc.name for desc, val in e.detail.ListFields()]:
            group = ET.SubElement(detail, "__group")
            if "name" in [desc.name for desc, val in e.detail.group.ListFields()]:
                group.set("name", e.detail.group.name)
            if "role" in [desc.name for desc, val in e.detail.group.ListFields()]:
                group.set("role", e.detail.group.role)
        if "precisionLocation" in [desc.name for desc, val in e.detail.ListFields()]:
            precisionlocation = ET.SubElement(detail, "precisionlocation")
            if "geopointsrc" in [desc.name for desc, val in e.detail.precisionLocation.ListFields()]:
                precisionlocation.set("geopointsrc", e.detail.precisionLocation.geopointsrc)
            if "altsrc" in [desc.name for desc, val in e.detail.precisionLocation.ListFields()]:
                precisionlocation.set("altsrc", e.detail.precisionLocation.altsrc)
        if "status" in [desc.name for desc, val in e.detail.ListFields()]:
            status = ET.SubElement(detail, "status")
            if "battery" in [desc.name for desc, val in e.detail.status.ListFields()]:
                status.set("battery", str(e.detail.status.battery))
        if "takv" in [desc.name for desc, val in e.detail.ListFields()]:
            takv = ET.SubElement(detail, "takv")
            if "device" in [desc.name for desc, val in e.detail.takv.ListFields()]:
                takv.set("device", e.detail.takv.device)
            if "platform" in [desc.name for desc, val in e.detail.takv.ListFields()]:
                takv.set("platform", e.detail.takv.platform)
            if "os" in [desc.name for desc, val in e.detail.takv.ListFields()]:
                takv.set("os", e.detail.takv.os)
            if "version" in [desc.name for desc, val in e.detail.takv.ListFields()]:
                takv.set("version", e.detail.takv.version)
        if "track" in [desc.name for desc, val in e.detail.ListFields()]:
            track = ET.SubElement(detail, "track")
            if "course" in [desc.name for desc, val in e.detail.track.ListFields()]:
                track.set("course", str(e.detail.track.course))
                track.set("speed", str(e.detail.track.speed))
    return ET.tostring(root)

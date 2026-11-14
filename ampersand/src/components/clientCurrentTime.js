"use client"

import { useEffect, useState } from "react";

export function getCurrentTimestampWithOffset() {
    const d = new Date();
    const pad = n => String(Math.abs(n)).padStart(2, '0');
    const off = -d.getTimezoneOffset(); // minutes east of UTC
    const sign = off >= 0 ? '+' : '-';

    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
        `T${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}` +
        `${sign}${pad(Math.trunc(off / 60))}:${pad(off % 60)}`;
}

export function ClientTimeZone() {
    const [detectedZone, setDetectedZone] = useState(null);

    useEffect(() => {
        const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        setDetectedZone(zone);
    }, []);

    return `${detectedZone}`;
}
"use client"

import { useEffect, useState } from "react";

export function ClientZoneNote({ note }) {
    const [detectedZone, setDetectedZone] = useState(null);

    useEffect(() => {
        const zone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        setDetectedZone(zone);
    }, []);

    return (
        detectedZone && <p>time: {new Date(note.time).toLocaleString(undefined, { timeZone: detectedZone })}</p>
    );
}





export function ClientZoneFront({ front, today, colors, index, zone }) {

    let targetOffsetMs = 0
    if (zone) {
        const targetOffset = new Date().toLocaleString("en-US", { timeZone: zone, timeZoneName: "short" }).split(" ")[2];
        targetOffsetMs = parseInt(targetOffset.slice(3, 6)) * 3600000;
    }

    let dayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime() + targetOffsetMs
    let DAY_MS = 24 * 60 * 60 * 1000
    let dayEnd = dayStart + DAY_MS


    let startTime = Math.max(new Date(front.start_time).getTime(), dayStart)
    let endTime = Math.min(front.end_time ? new Date(front.end_time).getTime() : Date.now(), dayEnd)
    if (endTime <= startTime) return null

    // let top = (((dayEnd - endTime) * 2 + 2 * 60 * 60 * 1000) / DAY_MS) * 100
    let top = (((dayEnd - endTime) * 2 + 2.75 * 60 * 60 * 1000) / DAY_MS) * 100
    let height = ((endTime - startTime) * 2 / DAY_MS) * 100
    return (
        <div key={front.front_id} className="absolute sm:left-1/2 w-4 sm:-translate-x-1/2 translate-x-3/4 rounded-2xl"
        style={{
            height: `${height}%`,
            top: `${top}%`,
            backgroundColor: colors[index%colors.length]
        }}
        />
    )
}
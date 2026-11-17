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
        const targetOffset = new Date().toLocaleString("en-US", { timeZone: zone, timeZoneName: "short" }).split(" ")[3]; //mst or other abbreviations
        console.log("targetOffset: ", targetOffset)
        targetOffsetMs = new Date(`1970-01-01T00:00:00${targetOffset}`).getTime()
    }

    console.log("targetOffsetMs: ", targetOffsetMs)

    let dayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
    let DAY_MS = 24 * 60 * 60 * 1000
    let dayEnd = dayStart + DAY_MS


    let startTime = Math.max(new Date(front.start_time).getTime(), dayStart) + targetOffsetMs
    let endTime = Math.min(front.end_time ? new Date(front.end_time).getTime() : Date.now(), dayEnd) + targetOffsetMs
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
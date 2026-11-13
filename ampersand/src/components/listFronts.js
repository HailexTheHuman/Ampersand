"use server"

import { setCookie } from "cookies-next/client";
import { cookies } from "next/headers";
import { connection } from "next/server";

export async function ListFronts({ username }) {
    await connection()
    
    const cookieStore = await cookies()
    let dayCookie = cookieStore.get("day")?.value
    let today = dayCookie ? new Date(dayCookie) : new Date()

    let resultsF = await fetch(`https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/get_front_history?username=${encodeURIComponent(username)}&year=${today.getFullYear()}&month=${today.getMonth()+1}&day=${today.getDate()}`, { cache: "no-store"})
    let frontsj = await resultsF.json();
    let fronts = frontsj.fronts


    let resultsA = await fetch(`https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let altersj = await resultsA.json();
    let alters = altersj.alters

    
    return (
        <FrontDivs alters={alters} fronts={fronts} today={today}/>
    )
}


async function FrontDivs({ alters, fronts, today }) {
    let dayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
    let DAY_MS = 24 * 60 * 60 * 1000
    let dayEnd = dayStart + DAY_MS
    let year = today.getFullYear()
    let month = today.getMonth()
    let date = today.getDate()
    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    let hours = ["Midnight", "11PM", "10PM", "9PM", "8PM", "7PM", "6PM", "5PM", "4PM", "3PM", "2PM", "1PM", "Noon", "11AM", "10AM", "9AM", "8AM", "7AM", "6AM", "5AM", "4AM", "3AM", "2AM", "1AM"]
    let colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    let alterI = 0
    return (
        <div className="relative flex flex-rows text-center w-[90%] h-[90%] border-1 outline-gray-600 border-gray-600 rounded-md overflow-y-auto overscroll-y-auto overflow-x-auto overscroll-x-auto  scrollbar-track-purple-100/0 scrollbar-thumb-purple-600 ">
            <div id="times" className="relative mx-[2%] h-[100%] min-w-[7%] w-[7%]">
                {/* <h4 className="fixed h-[10%] order-first">{months[month]} {date.toString()}, {year}</h4> */}
                {
                    hours.map((hour, index) => {
                        return (
                            <div key={hour} className="absolute sm:left-1/2 left-1 -translate-x-1/2"
                                style={{
                                    height: `${((DAY_MS/24) / DAY_MS) * 100}%`,
                                    top: `${((((index+1)*2*60*60*1000)) / DAY_MS) * 100}%`,
                                }}
                                >{hour}</div>
                        )
                    })
                }
                <h4 className="fixed order-first bg-black">{months[month]} {date.toString()}, {year}</h4>
            </div>
            {alters && alters.map((alter, index) => {
                alterI++
                return (
                    <div key={alter.alter_id} id={alter.alter} className="relative mx-[2%] h-[100%] min-w-[1%] w-[1%] ">
                        {/* <h4 className="fixed h-[10%] min-w-[1%] w-[1%] -translate-x-1/2 order-first">{alter.alter}</h4> */}
                        {fronts && fronts[alter.alter] && fronts[alter.alter].map((front) => {

                            let startTime = Math.max(new Date(front.start_time).getTime(), dayStart)
                            let endTime = Math.min(front.end_time ? new Date(front.end_time).getTime() : Date.now(), dayEnd)
                            if (endTime <= startTime) return null

                            // let top = (((dayEnd - endTime) * 2 + 2 * 60 * 60 * 1000) / DAY_MS) * 100
                            let top = (((dayEnd - endTime) * 2 + 2.75 * 60 * 60 * 1000) / DAY_MS) * 100
                            let height = ((endTime - startTime) * 2 / DAY_MS) * 100
                            return (
                                <div key={front.front_id} className="absolute sm:left-1/2 left-1 w-4 -translate-x-1/2 rounded-2xl"
                                style={{
                                    height: `${height}%`,
                                    top: `${top}%`,
                                    backgroundColor: colors[index%colors.length]
                                }}
                                />
                            )
                        })}
                        <h4 className="fixed min-w-[1%] w-[2%] max-w-[50%] sm:-translate-x-[50%] order-first bg-black" style={{color:alter.is_fronting ? "violet" : "white"}}>{alter.alter}</h4>
                    </div>
                )
            })}
        </div>
    )
}
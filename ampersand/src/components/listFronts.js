"use server"

import { setCookie } from "cookies-next/client";
import { cookies } from "next/headers";
import { connection } from "next/server";

export async function ListFronts({ username }) {
    await connection()
    
    const cookieStore = await cookies()
    let today = cookieStore.get("day")?.value
    if (!today) today = new Date()
    setCookie("day", today, {maxAge: 3600})

    console.log("username: ", username)
    let resultsF = await fetch(`http://localhost:8080/fronthistory?username=${encodeURIComponent(username)}&year=${today.getFullYear()}&month=${today.getMonth()+1}&day=${today.getDate()}`, { cache: "no-store"})
    let frontsj = await resultsF.json();
    let fronts = frontsj.fronts
    console.log("fronts: ", frontsj)


    let resultsA = await fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let altersj = await resultsA.json();
    let alters = altersj.alters
    console.log("alters: ", alters)

    
    return (
        <FrontDivs alters={alters} fronts={fronts} today={today}/>
    )
}

async function FrontDivs({ alters, fronts, today }) {
    let dayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime()
    let DAY_MS = 24 * 60 * 60 * 1000
    let dayEnd = dayStart + DAY_MS
    console.log("daystart, ", dayStart)
    console.log("daystart adjusted, ", dayStart)
    console.log("dayms, ", DAY_MS)
    let year = today.getFullYear()
    let month = today.getMonth()
    let date = today.getDate()
    let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    let hours = ["Midnight", "11PM", "10PM", "9PM", "8PM", "7PM", "6PM", "5PM", "4PM", "3PM", "2PM", "1PM", "Noon", "11AM", "10AM", "9AM", "8AM", "7AM", "6AM", "5AM", "4AM", "3AM", "2AM", "1AM"]
    let hoursInt = [24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    let colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    return (
        <div className="relative flex flex-rows text-center w-[90%] h-[90%] border-1 outline-gray-600 border-gray-600 rounded-md overflow-y-auto overscroll-y-auto overflow-x-auto overscroll-x-auto  scrollbar-track-purple-100/0 scrollbar-thumb-purple-600 ">
            <div id="times" className="relative mx-[2%] h-[100%] min-w-[7%] w-[7%]">
                <h4 className="h-[10%]">{months[month]} {date.toString()}, {year}</h4>
                {
                    hours.map((hour, index) => {
                        return (
                            // <p key={hour} className="h-[20%] my-[5%]">{hour}</p>
                            <div key={hour} className="absolute left-1/2 -translate-x-1/2 rounded-2xl"
                                style={{
                                    height: `${((DAY_MS/24) / DAY_MS) * 100}%`,
                                    top: `${((((index+1)*2*60*60*1000)) / DAY_MS) * 100}%`,
                                }}
                                >{hour}</div>
                        )
                    })
                }
            </div>
            {alters.map((alter, index) => {
                console.log("current alter: ", alter)
                return (
                    <div key={alter.alter_id} id={alter.alter} className="relative mx-[2%] h-[100%] min-w-[1%] w-[50%] ">
                        <h4 className="h-[10%]">{alter.alter}</h4>
                        {/* {
                            hours.map((hour) => {
                                let testClass = `h-[20%] my-[5%] w-[20%] mx-[40%] ${((hour.charCodeAt(0))%3==0 && (alter.alter.charCodeAt(0))%2==0) ? "bg-purple-500" : ""} rounded-2xl`
                                return (
                                    <div key={alter.alter+hour} id={alter.alter+hour} className={testClass}></div>
                                )
                            })
                        } */}
                        {fronts && fronts[alter.alter] && fronts[alter.alter].map((front) => {
                            let startTime = new Date(front.start_time).getTime() < dayStart ? dayStart : (new Date(front.start_time).getTime())
                            let endTime = front.end_time ? (new Date(front.end_time).getTime()) : (new Date().getTime())
                            // let timeTaken = ((endTime)-(startTime))
                            // let timeClass = `absolute bg-purple-600 h-[${((timeTaken)/DAY_MS)*100}%] text-purple-600 top-[${((dayEnd-endTime)/DAY_MS)*100}%] rounded-2xl`
                            return (
                                <div key={front.front_id} className="absolute left-1/2 w-4 -translate-x-1/2 rounded-2xl"
                                style={{
                                    height: `${((endTime - startTime)*2 / DAY_MS) * 100}%`,
                                    top: `${(((dayEnd - endTime)*2 + (2*60*60*1000)) / DAY_MS) * 100}%`,
                                    backgroundColor: colors[index]
                                }}
                                />
                            )
                        })}
                    </div>
                )
            })}
        </div>
    )
}
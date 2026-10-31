"use client"

import { setCookie } from "cookies-next/client"
import { useRouter } from "next/navigation";


export function setDay(router) {
    let chosenDate = document.getElementById('chooseDate').value;
    const [y, m, d] = chosenDate.split("-").map(Number)
    // let next = y+"-"+(m)+"-"+(d+1)
    const next = new Date(y, m - 1, d + 1)
    const fixedDate = [
        next.getFullYear(),
        String(next.getMonth() + 1).padStart(2, "0"),
        String(next.getDate()).padStart(2, "0"),
    ].join("-")

    console.log("fixed date: ", fixedDate)

    setCookie("day", fixedDate, {maxAge: 3600})
    router.refresh()
    
}



export function PickDay() {
    const router = useRouter()
    let maxdate = new Date()
    let maxdateString = `${maxdate.getFullYear()}-12-31`
    return (
        <form action={() => setDay(router)}>
            <label htmlFor="chooseDate">Select Date:</label>
            <input type="date" id="chooseDate" name="chooseDate" min="2026-10-01" max={maxdateString} required className="[&::-webkit-calendar-picker-indicator]:invert [&::-webkit-calendar-picker-indicator]:cursor-pointer" />
            <input type="submit"/>
        </form>
    )
}
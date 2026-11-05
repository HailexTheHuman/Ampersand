"use server"

import { cookies } from "next/headers";

export async function AuthorOptions() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value
    // console.log("username options: ", username)
    let results = await fetch(`https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let { alters } = await results.json();
    console.log("alters options: ", alters)
    return (
        <select name="author" id="author" placeholder="author" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[3%]" required>
            {await alters?.map((alter) => (
                <option key={alter.alter_id} value={alter.alter} className="text-gray-700 bg-purple-400">{alter.alter}</option>
            ))}
        </select>
    )
}

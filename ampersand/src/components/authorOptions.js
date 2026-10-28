"use server"

import { cookies } from "next/headers";

export async function AuthorOptions() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value
    // console.log("username options: ", username)
    let results = await fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
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



// // "use server"

// export function AuthorOptions({ username }) {
//     // console.log("username options: ", username)
//     // let results = await fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
//     // let { alters } = await results.json();
//     // console.log("alters options: ", alters)
//     var result;
//     var alters;
//     return fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"}).then((res) => {
//         alters=res.json()
//         return alters
//     }).then((alters) => {
//         console.log("alters options: ", alters.alters)
//         result = (
//             <select name="author" id="author" placeholder="author" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[3%]" required>
//                 {/* {await alters && alters.map((alter) => (
//                     <option key={alter.alter_id} value={alter.name}>{alter.name}</option>
//                 ))} */}
//                 {alters.alters?.map((alter) => (
//                     <option key={alter.alter_id} value={alter.alter} className="text-gray-700 bg-purple-400">{alter.alter}</option>
//                 ))}
//             </select>
//         )
//         console.log("result is: ", result)
//         return result
//     })
// }
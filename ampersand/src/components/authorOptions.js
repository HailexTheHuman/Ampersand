// "use server"

export function AuthorOptions({ username }) {
    // console.log("username options: ", username)
    // let results = await fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    // let { alters } = await results.json();
    // console.log("alters options: ", alters)
    fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"}).then((res) => {
        let alters=res.json()
        return alters
    }).then((alters) => {
        console.log("alters options: ", alters.alters)
        return (
            <select name="author" id="author" placeholder="author" className="border-2 outline-purple-700 border-purple-700 rounded-md ml-[3%]" required>
                {/* {await alters && alters.map((alter) => (
                    <option key={alter.alter_id} value={alter.name}>{alter.name}</option>
                ))} */}
                {alters.alters?.map((alter) => (
                    <option key={alter.alter_id} value={alter.alter} className="text-gray-700 bg-purple-400">{alter.alter}</option>
                ))}
            </select>
        )
    })
}
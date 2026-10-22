export async function ListAlters({ username }) {
    console.log("username: ", username)
    let results = await fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let altersj = await results.json();
    let alters = altersj.alters
    console.log("alters: ", alters)
    return (
        <div>
            {await alters && alters.map((alter) => (
                <div key={alter.alter_id} className="flex flex-col items-center text-center justify-between w-[20%] border-1 outline-gray-600 border-gray-600 rounded-md">
                    <p>name: {alter.alter}</p>
                    {alter.description && <p>description: {alter.description}</p>}
                </div>
            ))}
        </div>
    )
}
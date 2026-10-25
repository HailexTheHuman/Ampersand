import { SetFront } from "./setFront";

export async function ListAlters({ username }) {
    console.log("username: ", username)
    let results = await fetch(`http://localhost:8080/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let altersj = await results.json();
    let alters = altersj.alters
    console.log("alters: ", alters)
    return (
        // <div>
        <div className="flex flex-col items-center text-center justify-between w-[34%] border-1 outline-gray-600 border-gray-600 rounded-md overflow-y-auto overscroll-y-auto max-h-[90%] scrollbar-track-purple-100/0 scrollbar-thumb-purple-600 ">
            {await alters && alters.map((alter) => (
                <form key={alter.alter_id} className="flex flex-col items-center text-center justify-between w-[100%] border-1 outline-gray-600 border-gray-600 rounded-md" action={SetFront}>
                    <label htmlFor="name">name: </label>
                    <input type="text" name="name" id={alter.alter_id+"name"} value={alter.alter} readOnly/>
                    {alter.description && 
                    <div>
                        <label htmlFor="description">description: </label>
                        <input type="text" name="description" id={alter.alter_id+"description"} value={alter.description} readOnly/>
                    </div>
                    }
                    {alter.is_fronting && 
                    <div>
                        <label htmlFor="isFronting">is fronting: </label>
                        <input type="text" name="isFronting" id={alter.alter_id+"isFronting"} value={alter.is_fronting} readOnly/>
                    </div>
                    }
                    <input type="submit" name="submit" id="submit" value={"set to front"}/>
                </form>
            ))}
        </div>
    )
}
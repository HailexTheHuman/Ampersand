import { AddFront, RemoveFront, SetFront } from "./setFront";

export async function ListAlters({ username }) {
    let results = await fetch(`https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/alters?username=${encodeURIComponent(username)}`, { cache: "no-store"})
    let altersj = await results.json();
    let alters = altersj.alters
    return (
        <div className="flex flex-col items-center text-center justify-between sm:w-[34%] sm:border-1 outline-gray-600 border-gray-600 rounded-md overflow-y-visible sm:overflow-y-auto overscroll-y-auto sm:max-h-[90%] sm:h-[90%] h-[100%] scrollbar-track-purple-100/0 scrollbar-thumb-purple-600 sm:mr-[5%] resize-y sm:resize-none">
            {await alters && alters.map((alter) => (
                <div key={alter.alter_id} className="flex flex-col items-center text-center justify-between w-[100%] min-h-[25%] max-h-[100%] border-1 outline-gray-600 border-gray-600 rounded-md">
                    <form className="" style={{color:alter.is_fronting ? "violet" : "white"}} action={SetFront}>
                        <label htmlFor="name"></label>
                        <input type="text" name="name" id={alter.alter_id+"name"} value={alter.alter} readOnly className="text-center"/>
                        {/* {alter.description &&  */}
                        <div className="" >
                            <p id={alter.alter_id+"description"}> {alter.description} </p>
                        </div>
                        {/* } */}
                        {alter.is_fronting && 
                        <div>
                            <p id={alter.alter_id+"isFronting"}>is fronting</p>
                        </div>
                        }
                        <input type="submit" name="submit" id="submit" value={"set to front"} className={alter.is_fronting ? "hidden":"" }/>
                    </form>



                    <form className="" action={AddFront} style={{color:alter.is_fronting ? "violet" : "white"}}>
                        <label htmlFor="name" className="hidden">name: </label>
                        <input type="text" name="name" id={alter.alter_id+"name"} value={alter.alter} readOnly className="hidden"/>
                        <input type="submit" name="submit" id="submit" value={"add to front"} className={alter.is_fronting ? "hidden":"" }/>
                    </form>
                    <form className="" action={RemoveFront} style={{color:alter.is_fronting ? "violet" : "white"}}>
                        <label htmlFor="name" className="hidden">name: </label>
                        <input type="text" name="name" id={alter.alter_id+"name"} value={alter.alter} readOnly className="hidden"/>
                        <input type="submit" name="submit" id="submit" value={"Remove from front"} className={alter.is_fronting ? "":"hidden" }/>
                    </form>
                </div>
            ))}
        </div>
    )
}
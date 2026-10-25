import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { ListAlters } from "@/components/listAlters"
import { AddAlterForm, EditAlterForm } from "@/components/alterForms";
export const instant = false;
export default async function Page() {
    
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    const respone = await fetch(`http://localhost:8080/canPredict?username=${username}`);
    let jsonRes = await respone.json()
    const canPredict = jsonRes.can_predict

    if (!username) redirect("/login")
    
    console.log("username: ", username)
    console.log("response can predict: ", jsonRes)
    
    return (
        <main className="flex w-full w-[100%] max-h-[100%] h-[100%] flex-col items-center dark:bg-black">
            <h3 className="text-2xl text-center max-h-[10%]">Hello {username}</h3>
            <div className="flex flex-row max-h-[90%] h-[90%] max-w-[100%] w-[100%]">
                <ListAlters username={username}/>
                <div className="flex flex-col w-[100%] h-[100%]">
                    {canPredict && <a href="/identityCrisis" className="text-center">Who am I?</a>}
                    <div className="flex flex-row w-[100%] h-[90%] ">
                        <AddAlterForm username={username}/>
                        <EditAlterForm username={username}/>
                    </div>
                </div>
            </div>
        </main>
    )
}
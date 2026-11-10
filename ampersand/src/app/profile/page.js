import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { ListAlters } from "@/components/listAlters"
import { AddAlterForm, EditAlterForm } from "@/components/alterForms";
export const instant = false;
export default async function Page() {
    
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    // const respone = await fetch(`http://localhost:8080/canPredict?username=${username}`);
    const respone = await fetch(`https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/canPredict?username=${username}`);
    let jsonRes = await respone.json()
    const canPredict = jsonRes.can_predict

    if (!username) redirect("/login")
    
    return (
        <main className="sm:flex sm:w-full sm:w-[100%] sm:max-h-[79%] sm:h-[100%] sm:flex-col sm:items-center dark:bg-black sm:overflow-y-auto overflow-y-scroll overscroll-y-auto">
            <h3 className="text-2xl text-center max-h-[10%]">Hello {username}</h3>
            <div className="sm:flex sm:flex-row sm:max-h-[90%] h-[90%] max-w-[100%] w-[100%]">
                <div className="sm:flex sm:flex-row w-[100%] h-[100%]">
                    {canPredict && <a href="/identityCrisis" className="text-center">Who am I?</a>}
                    <div className="sm:flex sm:flex-row w-[100%] sm:h-[90%] h-[100%] ">
                        <AddAlterForm username={username}/>
                        <EditAlterForm username={username}/>
                    </div>
                </div>
                <ListAlters username={username} className=""/>
            </div>
        </main>
    )
}
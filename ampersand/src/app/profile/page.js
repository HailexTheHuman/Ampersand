import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { ListAlters } from "@/components/listAlters"
export const instant = false;
export default async function Page() {
    
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    if (!username) redirect("/login")
    
    console.log("username: ", username)
    
    return (
        <div>
            <h3 className="text-2xl text-center">Hello {username}</h3>
            <ListAlters username={username}/>
        </div>
    )
}
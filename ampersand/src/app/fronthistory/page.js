import { ListFronts } from "@/components/listFronts"
import { cookies } from "next/headers"
import { redirect } from "next/navigation";
export const instant = false;

export default async function Page() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    if (!username) redirect("/login")

    return (
        <div className="flex flex-col items-center w-full h-[78%]">
            <ListFronts username={username}/>
        </div>
    )
}
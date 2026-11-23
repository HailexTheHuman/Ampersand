import { ListFronts } from "@/components/listFronts"
import { PickDay } from "@/components/pickDay";
import { cookies } from "next/headers"
import { redirect } from "next/navigation";
import { headers } from "next/headers"
import { userAgentFromString } from "next/server";
// import { osDetector } from "@/components/clientOSDetecter";
export const instant = false;

export default async function Page() {
    const cookieStore = await cookies()
    const username = cookieStore.get("username")?.value

    if (!username) redirect("/login")

    // const os = osDetector();

    const headersList = await headers();
    const uaString = headersList.get('user-agent') || undefined;
    const { os } = userAgentFromString(uaString);
    

    return (
        <div className={ (os.name === "macOS" || os.name === "Windows" || os.name === "Linux") ? "flex flex-col items-center w-full h-[78%]" : "flex flex-col items-center w-full h-[78%] sm:h-[400]" }>
            <h2>Front History</h2>
            <PickDay />
            <ListFronts username={username} os={os}/>
        </div>
    )
}
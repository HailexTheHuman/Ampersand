"use client"

import { hasCookie, deleteCookie, getCookie } from "cookies-next/client";
import { redirect, useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Page() {
    let has = hasCookie("username")
    deleteCookie("username")
    has = hasCookie("username")
    
    if (!has) {
        const router = useRouter();
        useEffect(() => {
        async function logout() {
            await router.refresh();
            await router.push('/');
        }
        logout();
    }, [router]);
    }
    return (
        <p>logging out</p>
    )
}
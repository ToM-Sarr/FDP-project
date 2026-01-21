import React from "react";

export default function Navbar() {
  return (
    <nav className="w-full bg-white dark:bg-black border-b border-black/[.08] dark:border-white/[.145]">

        <div className="p-4 flex items-center justify-between mx-auto">    
            <div className="text-2xl px-6 font-semibold text-black dark:text-zinc-50">
                Lesa
            </div>  
            <div className="flex items-center gap-8">
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    Menu
                </a>
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    Histoire
                </a>
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    Contact
                </a>
            </div>
            <div className="flex items-center gap-6">
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    <img src="/facebook.svg" alt="Facebook" className="w-5 h-5" />
                </a>
                <a aria-label="Instagram" href="#" className="text-black dark:text-zinc-50 hover:underline">
                    Instagram
                </a>
                <a aria-label="TikTok" href="#" className="text-black dark:text-zinc-50 hover:underline">
                    TikTok
                </a>
            </div>
        </div>
    </nav>
  );
}
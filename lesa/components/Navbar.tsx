export default function Navbar() {
  return (
    <nav className="w-full bg-white dark:bg-black border-b border-black/[.08] dark:border-white/[.145]">

        <div className="p-6 flex items-center justify-between mx-auto">    
            <div className="text-2xl px-6 font-semibold text-black dark:text-zinc-50">
                Lesa
            </div>  
            <div className="flex items-center gap-6">
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    Home

                </a>
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    About
                </a>
                <a href="#" className="text-black dark:text-zinc-50 hover:underline">
                    Contact
                </a>
            </div>
        </div>
    </nav>
  );
}
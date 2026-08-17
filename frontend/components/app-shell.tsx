"use client";
import Link from "next/link";
import { Bell, ClipboardList, Home, Megaphone, PackageSearch, Plus, Settings, UserRound, Orbit } from "lucide-react";
import type { ReactNode } from "react";

const links=[['/dashboard','Overview',Home],['/complaints','Complaints',ClipboardList],['/complaints/new','Raise issue',Plus],['/lost-found','Lost & Found',PackageSearch],['/announcements','Announcements',Megaphone],['/notifications','Notifications',Bell],['/profile','Profile',UserRound]] as const;
export function Brand(){return <span className="brand-lockup"><i className="logo"><Orbit/></i>campus<span>os</span></span>}
export function AppShell({title,children,action}:{title:string;children:ReactNode;action?:ReactNode}){return <main className="app"><header className="topbar"><Link href="/dashboard"><Brand/></Link><div className="top-actions">{action}<Link className="icon-button" href="/notifications" aria-label="Notifications"><Bell size={18}/></Link><button className="avatar" onClick={()=>{sessionStorage.removeItem('campusos_access');location.href='/login'}}>CS</button></div></header><div className="app-grid"><aside className="sidebar"><p className="nav-label">WORKSPACE</p>{links.map(([href,label,Icon])=><Link href={href} key={href}><Icon size={17}/><span>{label}</span></Link>)}<p className="nav-label">ACCOUNT</p><Link href="/profile"><Settings size={17}/><span>Settings</span></Link></aside><section className="content"><div className="page-heading"><div><p className="eyebrow">CAMPUS OPERATIONS</p><h1>{title}</h1></div>{action}</div>{children}</section></div></main>}

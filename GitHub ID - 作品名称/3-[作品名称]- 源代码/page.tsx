'use client';
import { useRouter } from 'next/navigation';
export default function Index() {
    const router = useRouter();
    router.replace('/cn');
    return <div></div>;
}

import { useEffect } from "react";
import { useRouter } from "next/router";
import jwt_decode from "jwt-decode";

export default function AuthGuard({ children }) {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      router.push("/login");
    } else {
      try {
        const decoded = jwt_decode(token);
        const userRole = decoded.role;

        if (router.pathname.startsWith("/provider-dashboard") && userRole !== "provider") {
          router.push("/patient-dashboard");
        } else if (router.pathname.startsWith("/patient-dashboard") && userRole !== "patient") {
          router.push("/provider-dashboard");
        }
      } catch (error) {
        localStorage.removeItem("token");
        router.push("/login");
      }
    }
  }, [router]);

  return children;
}

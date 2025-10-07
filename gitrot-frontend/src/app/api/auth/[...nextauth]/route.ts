import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import type { NextAuthOptions } from "next-auth";
import { authApi } from "@/lib/api/auth";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user, account }) {
      try {
        if (!user.email) {
          console.log("No email provider by OAuth provider");
          return false;
        }

        const response = await authApi.registerOrLogin({
          email: user.email,
          name: user.name,
          image: user.image,
          provider: account?.provider || "google",
          provider_id: account?.providerAccountId || user.id,
        });

        console.log("Response", response);

        user.id = response.user_id;

        console.log(
          `User ${response.isNew ? "registered" : "logged in"}: ${
            response.email
          }`
        );
        return true;
      } catch (error) {
        console.log("Error during sign in:", error);
        return false;
      }
    },
    async session({ session, token }) {
      // Add user id to session
      if (session.user) {
        session.user.id = token.sub!;
      }
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id;
      }
      return token;
    },
  },
  pages: {
    signIn: "/", // Redirect to home page for sign in
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };

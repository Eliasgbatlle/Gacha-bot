import DiscordProvider from "next-auth/providers/discord";
import { Session, User } from "next-auth";
import { JWT } from "next-auth/jwt";

export const authOptions = {
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID as string,
      clientSecret: process.env.DISCORD_CLIENT_SECRET as string,
    }),
  ],
  secret: process.env.NEXTAUTH_SECRET,
  callbacks: {
    async session({ session, token }: { session: Session; token: JWT }) {
      if (token && token.sub) {
        (session.user as User).id = token.sub;
      }
      return session;
    },
  },
};
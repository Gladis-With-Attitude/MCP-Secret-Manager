"use client";

import { type FormEvent, useState } from "react";

import { useRouter } from "next/navigation";

import { KeyRound, LogIn } from "lucide-react";

import { BreadcrumbBar } from "@/components/app-shell/breadcrumb-bar";
import { PublicLayout } from "@/components/app-shell/public-layout";
import { Button } from "@/components/buttons/button";
import { Card } from "@/components/display/card";
import { ErrorState } from "@/components/feedback/error-state";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { PageHeader } from "@/components/layout/page-header";
import { useAuth } from "@/hooks/use-auth";

export default function Home() {
  const auth = useAuth();
  const router = useRouter();
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await auth.loginWithApiKey(apiKey);
      router.push("/dashboard");
    } catch (caughtError) {
      if (caughtError instanceof Error) {
        setError(caughtError.message);
      } else {
        setError("Authentication failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PublicLayout>
      <div className="grid min-h-[70vh] content-center gap-6">
        <PageHeader
          breadcrumb={<BreadcrumbBar />}
          description="Use a generated API key to open an authenticated administration session."
          title="MCP Secret Manager"
        />
        <Card className="max-w-xl">
          <form className="grid gap-4" onSubmit={(event) => void handleSubmit(event)}>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-md bg-secondary text-secondary-foreground">
                <KeyRound aria-hidden="true" className="size-5" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-foreground">Sign in</h2>
                <p className="text-sm text-muted-foreground">API key session</p>
              </div>
            </div>
            <FormField
              description="The key is exchanged for an HTTP-only browser session."
              error={error}
              id="api-key"
              label="API key"
            >
              <Input
                aria-invalid={Boolean(error)}
                autoComplete="off"
                id="api-key"
                onChange={(event) => setApiKey(event.target.value)}
                placeholder="mcp_sm_..."
                spellCheck={false}
                type="password"
                value={apiKey}
              />
            </FormField>
            <Button disabled={!apiKey.trim()} fullWidth isLoading={isSubmitting} type="submit">
              <LogIn aria-hidden="true" className="size-4" />
              Sign in
            </Button>
          </form>
        </Card>
        {auth.isAuthenticated ? (
          <ErrorState
            action={
              <Button onClick={() => router.push("/dashboard")} variant="outline">
                Continue to dashboard
              </Button>
            }
            description="This browser already has an active API key session."
            title="Session active"
          />
        ) : null}
      </div>
    </PublicLayout>
  );
}

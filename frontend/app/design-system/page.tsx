"use client";

import { useState } from "react";

import { Check, RefreshCw, Search, Settings, Trash2 } from "lucide-react";

import { Button } from "@/components/buttons/button";
import { IconButton } from "@/components/buttons/icon-button";
import { DataTable, type DataTableColumn } from "@/components/data-display/data-table";
import { Badge } from "@/components/display/badge";
import { Card } from "@/components/display/card";
import { Divider } from "@/components/display/divider";
import { EmptyState } from "@/components/feedback/empty-state";
import { ErrorState } from "@/components/feedback/error-state";
import { ForbiddenState } from "@/components/feedback/forbidden-state";
import { LoadingState } from "@/components/feedback/loading-state";
import { Skeleton } from "@/components/feedback/skeleton";
import { Spinner } from "@/components/feedback/spinner";
import { Checkbox } from "@/components/forms/checkbox";
import { FieldError } from "@/components/forms/field-error";
import { FormField } from "@/components/forms/form-field";
import { Input } from "@/components/forms/input";
import { RadioGroup } from "@/components/forms/radio-group";
import { Select } from "@/components/forms/select";
import { Switch } from "@/components/forms/switch";
import { Textarea } from "@/components/forms/textarea";
import { Container } from "@/components/layout/container";
import { Grid } from "@/components/layout/grid";
import { Page } from "@/components/layout/page";
import { PageHeader } from "@/components/layout/page-header";
import { Section } from "@/components/layout/section";
import { Stack } from "@/components/layout/stack";
import { Breadcrumb } from "@/components/navigation/breadcrumb";
import { Pagination } from "@/components/navigation/pagination";
import { Tabs } from "@/components/navigation/tabs";
import { ConfirmDialog } from "@/components/overlay/confirm-dialog";
import { Dialog } from "@/components/overlay/dialog";
import { Drawer } from "@/components/overlay/drawer";
import { Tooltip } from "@/components/overlay/tooltip";
import { Heading } from "@/components/typography/heading";
import { Label } from "@/components/typography/label";
import { Text } from "@/components/typography/text";

type DemoRow = {
  id: string;
  name: string;
  status: string;
};

const rows: DemoRow[] = [
  { id: "1", name: "Alpha", status: "Ready" },
  { id: "2", name: "Beta", status: "Paused" },
];

const columns: DataTableColumn<DemoRow>[] = [
  {
    cell: (row) => row.name,
    header: "Name",
    key: "name",
  },
  {
    cell: (row) => (
      <Badge variant={row.status === "Ready" ? "success" : "warning"}>{row.status}</Badge>
    ),
    header: "Status",
    key: "status",
  },
  {
    cell: () => (
      <div className="flex justify-end gap-1">
        <IconButton
          icon={<Settings className="size-4" />}
          label="Open row actions"
          variant="table"
        />
      </div>
    ),
    className: "text-right",
    header: "Actions",
    headerClassName: "text-right",
    key: "actions",
  },
];

export default function DesignSystemPage() {
  const [checked, setChecked] = useState(false);
  const [enabled, setEnabled] = useState(false);
  const [radioValue, setRadioValue] = useState("one");
  const [selectValue, setSelectValue] = useState("alpha");

  return (
    <Page>
      <Container size="xl">
        <Stack gap="xl">
          <PageHeader
            breadcrumb={
              <Breadcrumb items={[{ href: "/", label: "Home" }, { label: "Design System" }]} />
            }
            description="Temporary development page for generic components."
            title="Design System"
          />

          <Section title="Buttons">
            <Stack>
              <div className="flex flex-wrap gap-3">
                <Button>Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Danger</Button>
                <Button isLoading>Loading</Button>
              </div>
              <div className="flex flex-wrap gap-2">
                <IconButton
                  icon={<Check className="size-4" />}
                  label="Default action"
                  variant="default"
                />
                <IconButton icon={<Search className="size-4" />} label="Search" variant="ghost" />
                <IconButton
                  icon={<Settings className="size-4" />}
                  label="Settings"
                  variant="outline"
                />
                <IconButton
                  icon={<Trash2 className="size-4" />}
                  label="Danger action"
                  variant="danger"
                />
                <IconButton
                  icon={<RefreshCw className="size-4" />}
                  label="Table action"
                  variant="table"
                />
                <IconButton
                  icon={<Settings className="size-4" />}
                  label="Toolbar action"
                  variant="toolbar"
                />
              </div>
            </Stack>
          </Section>

          <Section title="Badges and Display">
            <Stack>
              <div className="flex flex-wrap gap-2">
                <Badge>Neutral</Badge>
                <Badge variant="info">Info</Badge>
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="danger">Danger</Badge>
              </div>
              <Grid columns={3}>
                <Card>
                  <Heading as="h3" size="sm">
                    Default card
                  </Heading>
                  <Text tone="muted">Reusable framed content.</Text>
                </Card>
                <Card variant="summary">
                  <Heading as="h3" size="sm">
                    Summary card
                  </Heading>
                  <Text tone="muted">Compact information block.</Text>
                </Card>
                <Card variant="empty">
                  <Heading as="h3" size="sm">
                    Empty card
                  </Heading>
                  <Text tone="muted">Quiet placeholder surface.</Text>
                </Card>
              </Grid>
              <Divider />
            </Stack>
          </Section>

          <Section title="Typography">
            <Stack gap="sm">
              <Heading as="h1" size="xl">
                Heading xl
              </Heading>
              <Heading as="h2" size="lg">
                Heading lg
              </Heading>
              <Heading as="h3" size="md">
                Heading md
              </Heading>
              <Text>Default text for interface content.</Text>
              <Text tone="muted">Muted text for supporting content.</Text>
              <Label>Field label</Label>
            </Stack>
          </Section>

          <Section title="Forms">
            <Grid columns={2}>
              <FormField description="Short helper text." id="demo-input" label="Input" required>
                <Input id="demo-input" placeholder="Text value" />
              </FormField>
              <FormField id="demo-select" label="Select">
                <Select
                  id="demo-select"
                  onValueChange={setSelectValue}
                  options={[
                    { label: "Alpha", value: "alpha" },
                    { label: "Beta", value: "beta" },
                    { label: "Gamma", value: "gamma" },
                  ]}
                  value={selectValue}
                />
              </FormField>
              <FormField id="demo-textarea" label="Textarea">
                <Textarea id="demo-textarea" placeholder="Longer value" />
              </FormField>
              <Stack>
                <Checkbox
                  checked={checked}
                  label="Checkbox"
                  onCheckedChange={(value) => setChecked(value === true)}
                />
                <Switch checked={enabled} label="Switch" onCheckedChange={setEnabled} />
                <RadioGroup
                  onValueChange={setRadioValue}
                  options={[
                    { label: "Option one", value: "one" },
                    { description: "Secondary detail.", label: "Option two", value: "two" },
                  ]}
                  value={radioValue}
                />
                <FieldError>Validation message.</FieldError>
              </Stack>
            </Grid>
          </Section>

          <Section title="Feedback">
            <Grid columns={4}>
              <LoadingState title="Loading content" />
              <EmptyState description="There is nothing to show yet." title="No content" />
              <ErrorState description="Try again later." title="Unable to load" />
              <ForbiddenState />
            </Grid>
            <div className="flex items-center gap-4">
              <Spinner />
              <Skeleton className="h-4 w-48" />
            </div>
          </Section>

          <Section title="Overlays">
            <div className="flex flex-wrap gap-3">
              <Dialog
                description="This dialog uses a generic title, description, content and footer."
                footer={<Button>Continue</Button>}
                title="Dialog title"
                trigger={<Button variant="outline">Open dialog</Button>}
              >
                Dialog content.
              </Dialog>
              <ConfirmDialog
                description="Confirm this generic operation."
                onConfirm={() => undefined}
                title="Confirm action"
                trigger={<Button variant="outline">Open confirmation</Button>}
              />
              <Drawer
                description="This drawer displays contextual generic content."
                title="Drawer title"
                trigger={<Button variant="outline">Open drawer</Button>}
              >
                Drawer content.
              </Drawer>
              <Tooltip content="Tooltip content">
                <Button variant="ghost">Hover tooltip</Button>
              </Tooltip>
            </div>
          </Section>

          <Section title="Data Display">
            <Stack>
              <DataTable
                caption="Demo table"
                columns={columns}
                data={rows}
                getRowKey={(row) => row.id}
              />
              <Pagination
                isPreviousDisabled
                onNext={() => undefined}
                onPrevious={() => undefined}
                pageLabel="Page 1 of 3"
              />
            </Stack>
          </Section>

          <Section title="Tabs">
            <Tabs
              items={[
                { content: <Text>First panel.</Text>, label: "First", value: "first" },
                { content: <Text>Second panel.</Text>, label: "Second", value: "second" },
              ]}
            />
          </Section>
        </Stack>
      </Container>
    </Page>
  );
}

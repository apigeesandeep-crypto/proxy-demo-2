#!/usr/bin/env python3
"""
generate_xml.py
Generates all required XML configuration files for the Apigee proxy-demo-2 bundle.
"""

import os
import sys
import textwrap

PROXY_NAME = "proxy-demo-2"


# ─────────────────────────────────────────────
# XML content definitions
# ─────────────────────────────────────────────

def proxy_descriptor_xml() -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <APIProxy revision="1" name="{PROXY_NAME}">
            <DisplayName>{PROXY_NAME}</DisplayName>
            <Description>Demo API Proxy with AssignMessage policies</Description>
            <BasePaths>/{PROXY_NAME}</BasePaths>

            <Policies>
                <Policy>AM-SetRequestHeaders</Policy>
                <Policy>AM-SetResponsePayload</Policy>
                <Policy>RF-MethodNotAllowed</Policy>
            </Policies>

            <ProxyEndpoints>
                <ProxyEndpoint>default</ProxyEndpoint>
            </ProxyEndpoints>

            <TargetEndpoints>
                <TargetEndpoint>default</TargetEndpoint>
            </TargetEndpoints>
        </APIProxy>
    """)


def proxy_endpoint_xml() -> str:
    return textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ProxyEndpoint name="default">

            <Description>Default Proxy Endpoint – request/response AssignMessage</Description>

            <PreFlow name="PreFlow">
                <Request>
                    <Step>
                        <Name>AM-SetRequestHeaders</Name>
                    </Step>
                </Request>
                <Response/>
            </PreFlow>

            <Flows>

                <Flow name="Allow-GET">
                    <Condition>(request.verb = "GET")</Condition>
                </Flow>

                <Flow name="Reject-NonGET">
                    <Condition>(request.verb != "GET")</Condition>
                    <Request>
                        <Step>
                            <Name>RF-MethodNotAllowed</Name>
                        </Step>
                    </Request>
                </Flow>

            </Flows>

            <PostFlow name="PostFlow">
                <Request/>
                <Response>
                    <Step>
                        <Name>AM-SetResponsePayload</Name>
                    </Step>
                </Response>
            </PostFlow>

            <HTTPProxyConnection>
                <BasePath>/{PROXY_NAME}</BasePath>
                <VirtualHost>secure</VirtualHost>
            </HTTPProxyConnection>

            <RouteRule name="default">
                <TargetEndpoint>default</TargetEndpoint>
            </RouteRule>

        </ProxyEndpoint>
    """)


def target_endpoint_xml() -> str:
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <TargetEndpoint name="default">
            <Description>Default Target Endpoint</Description>

            <PreFlow name="PreFlow">
                <Request/>
                <Response/>
            </PreFlow>

            <PostFlow name="PostFlow">
                <Request/>
                <Response/>
            </PostFlow>

            <HTTPTargetConnection>
                <URL>https://mocktarget.apigee.net</URL>
            </HTTPTargetConnection>
        </TargetEndpoint>
    """)


def assign_message_request_xml() -> str:
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <AssignMessage name="AM-SetRequestHeaders" continueOnError="false" enabled="true">
            <DisplayName>AM-SetRequestHeaders</DisplayName>

            <Add>
                <Headers>
                    <Header name="X-Proxy-Name">proxy-demo-2</Header>
                    <Header name="X-Forwarded-By">apigee-gateway</Header>
                    <Header name="X-Request-ID">{messageid}</Header>
                    <Header name="X-Environment">{environment.name}</Header>
                </Headers>
            </Add>

            <Remove>
                <Headers>
                    <Header name="X-Internal-Token"/>
                </Headers>
            </Remove>

            <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
            <AssignTo createNew="false" transport="http" type="request"/>
        </AssignMessage>
    """)


def assign_message_response_xml() -> str:
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <AssignMessage name="AM-SetResponsePayload" continueOnError="false" enabled="true">
            <DisplayName>AM-SetResponsePayload</DisplayName>

            <Set>
                <Headers>
                    <Header name="Content-Type">application/json</Header>
                    <Header name="X-Powered-By">Apigee</Header>
                </Headers>

                <Payload contentType="application/json">
                    {
                        "status": "success",
                        "proxy": "{proxy.name}",
                        "path": "{proxy.pathsuffix}",
                        "method": "{request.verb}",
                        "messageId": "{messageid}",
                        "environment": "{environment.name}",
                        "target": "{target.url}"
                    }
                </Payload>

                <StatusCode>200</StatusCode>
                <ReasonPhrase>OK</ReasonPhrase>
            </Set>

            <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
            <AssignTo createNew="false" transport="http" type="response"/>
        </AssignMessage>
    """)


def rf_method_not_allowed_xml() -> str:
    """New policy: RF-MethodNotAllowed (405 response)"""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <AssignMessage name="RF-MethodNotAllowed" continueOnError="false" enabled="true">
            <DisplayName>RF-MethodNotAllowed</DisplayName>

            <Set>
                <Headers>
                    <Header name="Content-Type">application/json</Header>
                </Headers>

                <Payload contentType="application/json">
                    {
                        "error": "Method Not Allowed",
                        "allowed": "GET",
                        "received": "{request.verb}"
                    }
                </Payload>

                <StatusCode>405</StatusCode>
                <ReasonPhrase>Method Not Allowed</ReasonPhrase>
            </Set>

            <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
            <AssignTo createNew="true" transport="http" type="response"/>
        </AssignMessage>
    """)


# ─────────────────────────────────────────────
# File manifest
# ─────────────────────────────────────────────

FILE_MANIFEST = [
    (f"apiproxy/{PROXY_NAME}.xml", proxy_descriptor_xml),
    ("apiproxy/proxies/default.xml", proxy_endpoint_xml),
    ("apiproxy/targets/default.xml", target_endpoint_xml),
    ("apiproxy/policies/AM-SetRequestHeaders.xml", assign_message_request_xml),
    ("apiproxy/policies/AM-SetResponsePayload.xml", assign_message_response_xml),
    ("apiproxy/policies/RF-MethodNotAllowed.xml", rf_method_not_allowed_xml),
]


def write_files(base_path: str = ".") -> None:
    for relative_path, content_fn in FILE_MANIFEST:
        full_path = os.path.join(base_path, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as fh:
            fh.write(content_fn())
        print(f"[OK] Written: {full_path}")


def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"==> Generating XML files under: {os.path.abspath(base_path)}")
    write_files(base_path)
    print("==> XML generation complete.")


if __name__ == "__main__":
    main()

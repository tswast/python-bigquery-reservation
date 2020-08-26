# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.bigquery.reservation_v1.services.reservation_service import (
    ReservationServiceAsyncClient,
)
from google.cloud.bigquery.reservation_v1.services.reservation_service import (
    ReservationServiceClient,
)
from google.cloud.bigquery.reservation_v1.services.reservation_service import pagers
from google.cloud.bigquery.reservation_v1.services.reservation_service import transports
from google.cloud.bigquery.reservation_v1.types import reservation
from google.cloud.bigquery.reservation_v1.types import reservation as gcbr_reservation
from google.oauth2 import service_account
from google.protobuf import any_pb2 as any  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.rpc import status_pb2 as status  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert ReservationServiceClient._get_default_mtls_endpoint(None) is None
    assert (
        ReservationServiceClient._get_default_mtls_endpoint(api_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ReservationServiceClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        ReservationServiceClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ReservationServiceClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        ReservationServiceClient._get_default_mtls_endpoint(non_googleapi)
        == non_googleapi
    )


@pytest.mark.parametrize(
    "client_class", [ReservationServiceClient, ReservationServiceAsyncClient]
)
def test_reservation_service_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "bigqueryreservation.googleapis.com:443"


def test_reservation_service_client_get_transport_class():
    transport = ReservationServiceClient.get_transport_class()
    assert transport == transports.ReservationServiceGrpcTransport

    transport = ReservationServiceClient.get_transport_class("grpc")
    assert transport == transports.ReservationServiceGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ReservationServiceClient, transports.ReservationServiceGrpcTransport, "grpc"),
        (
            ReservationServiceAsyncClient,
            transports.ReservationServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    ReservationServiceClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ReservationServiceClient),
)
@mock.patch.object(
    ReservationServiceAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(ReservationServiceAsyncClient),
)
def test_reservation_service_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(ReservationServiceClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(ReservationServiceClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                client_cert_source=client_cert_source_callback,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", and default_client_cert_source is provided.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_MTLS_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_MTLS_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case api_endpoint is not provided, GOOGLE_API_USE_MTLS is
    # "auto", but client_cert_source and default_client_cert_source are None.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "auto"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class()
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client.DEFAULT_ENDPOINT,
                    scopes=None,
                    api_mtls_endpoint=client.DEFAULT_ENDPOINT,
                    client_cert_source=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ReservationServiceClient, transports.ReservationServiceGrpcTransport, "grpc"),
        (
            ReservationServiceAsyncClient,
            transports.ReservationServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_reservation_service_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (ReservationServiceClient, transports.ReservationServiceGrpcTransport, "grpc"),
        (
            ReservationServiceAsyncClient,
            transports.ReservationServiceGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_reservation_service_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            api_mtls_endpoint=client.DEFAULT_ENDPOINT,
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_reservation_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.bigquery.reservation_v1.services.reservation_service.transports.ReservationServiceGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = ReservationServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            api_mtls_endpoint="squid.clam.whelk",
            client_cert_source=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_create_reservation(
    transport: str = "grpc", request_type=gcbr_reservation.CreateReservationRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcbr_reservation.Reservation(
            name="name_value", slot_capacity=1391, ignore_idle_slots=True,
        )

        response = client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == gcbr_reservation.CreateReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcbr_reservation.Reservation)

    assert response.name == "name_value"

    assert response.slot_capacity == 1391

    assert response.ignore_idle_slots is True


def test_create_reservation_from_dict():
    test_create_reservation(request_type=dict)


@pytest.mark.asyncio
async def test_create_reservation_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = gcbr_reservation.CreateReservationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcbr_reservation.Reservation(
                name="name_value", slot_capacity=1391, ignore_idle_slots=True,
            )
        )

        response = await client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcbr_reservation.Reservation)

    assert response.name == "name_value"

    assert response.slot_capacity == 1391

    assert response.ignore_idle_slots is True


def test_create_reservation_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = gcbr_reservation.CreateReservationRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_reservation), "__call__"
    ) as call:
        call.return_value = gcbr_reservation.Reservation()

        client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_reservation_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = gcbr_reservation.CreateReservationRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_reservation), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcbr_reservation.Reservation()
        )

        await client.create_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_reservation_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcbr_reservation.Reservation()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_reservation(
            parent="parent_value",
            reservation=gcbr_reservation.Reservation(name="name_value"),
            reservation_id="reservation_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].reservation == gcbr_reservation.Reservation(name="name_value")

        assert args[0].reservation_id == "reservation_id_value"


def test_create_reservation_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_reservation(
            gcbr_reservation.CreateReservationRequest(),
            parent="parent_value",
            reservation=gcbr_reservation.Reservation(name="name_value"),
            reservation_id="reservation_id_value",
        )


@pytest.mark.asyncio
async def test_create_reservation_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcbr_reservation.Reservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcbr_reservation.Reservation()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_reservation(
            parent="parent_value",
            reservation=gcbr_reservation.Reservation(name="name_value"),
            reservation_id="reservation_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].reservation == gcbr_reservation.Reservation(name="name_value")

        assert args[0].reservation_id == "reservation_id_value"


@pytest.mark.asyncio
async def test_create_reservation_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_reservation(
            gcbr_reservation.CreateReservationRequest(),
            parent="parent_value",
            reservation=gcbr_reservation.Reservation(name="name_value"),
            reservation_id="reservation_id_value",
        )


def test_list_reservations(
    transport: str = "grpc", request_type=reservation.ListReservationsRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reservations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListReservationsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.ListReservationsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReservationsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_reservations_from_dict():
    test_list_reservations(request_type=dict)


@pytest.mark.asyncio
async def test_list_reservations_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.ListReservationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reservations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListReservationsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListReservationsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_reservations_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.ListReservationsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reservations), "__call__"
    ) as call:
        call.return_value = reservation.ListReservationsResponse()

        client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_reservations_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.ListReservationsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reservations), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListReservationsResponse()
        )

        await client.list_reservations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_reservations_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reservations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListReservationsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_reservations(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_reservations_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_reservations(
            reservation.ListReservationsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_reservations_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reservations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListReservationsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListReservationsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_reservations(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_reservations_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_reservations(
            reservation.ListReservationsRequest(), parent="parent_value",
        )


def test_list_reservations_pager():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reservations), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListReservationsResponse(
                reservations=[
                    reservation.Reservation(),
                    reservation.Reservation(),
                    reservation.Reservation(),
                ],
                next_page_token="abc",
            ),
            reservation.ListReservationsResponse(
                reservations=[], next_page_token="def",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(),], next_page_token="ghi",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(), reservation.Reservation(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_reservations(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, reservation.Reservation) for i in results)


def test_list_reservations_pages():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_reservations), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListReservationsResponse(
                reservations=[
                    reservation.Reservation(),
                    reservation.Reservation(),
                    reservation.Reservation(),
                ],
                next_page_token="abc",
            ),
            reservation.ListReservationsResponse(
                reservations=[], next_page_token="def",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(),], next_page_token="ghi",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(), reservation.Reservation(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_reservations(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_reservations_async_pager():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reservations),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListReservationsResponse(
                reservations=[
                    reservation.Reservation(),
                    reservation.Reservation(),
                    reservation.Reservation(),
                ],
                next_page_token="abc",
            ),
            reservation.ListReservationsResponse(
                reservations=[], next_page_token="def",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(),], next_page_token="ghi",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(), reservation.Reservation(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_reservations(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, reservation.Reservation) for i in responses)


@pytest.mark.asyncio
async def test_list_reservations_async_pages():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_reservations),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListReservationsResponse(
                reservations=[
                    reservation.Reservation(),
                    reservation.Reservation(),
                    reservation.Reservation(),
                ],
                next_page_token="abc",
            ),
            reservation.ListReservationsResponse(
                reservations=[], next_page_token="def",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(),], next_page_token="ghi",
            ),
            reservation.ListReservationsResponse(
                reservations=[reservation.Reservation(), reservation.Reservation(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_reservations(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_reservation(
    transport: str = "grpc", request_type=reservation.GetReservationRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_reservation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Reservation(
            name="name_value", slot_capacity=1391, ignore_idle_slots=True,
        )

        response = client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.GetReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.Reservation)

    assert response.name == "name_value"

    assert response.slot_capacity == 1391

    assert response.ignore_idle_slots is True


def test_get_reservation_from_dict():
    test_get_reservation(request_type=dict)


@pytest.mark.asyncio
async def test_get_reservation_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.GetReservationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Reservation(
                name="name_value", slot_capacity=1391, ignore_idle_slots=True,
            )
        )

        response = await client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.Reservation)

    assert response.name == "name_value"

    assert response.slot_capacity == 1391

    assert response.ignore_idle_slots is True


def test_get_reservation_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.GetReservationRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_reservation), "__call__") as call:
        call.return_value = reservation.Reservation()

        client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_reservation_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.GetReservationRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_reservation), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Reservation()
        )

        await client.get_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_reservation_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_reservation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Reservation()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_reservation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_reservation_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_reservation(
            reservation.GetReservationRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_reservation_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Reservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Reservation()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_reservation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_reservation_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_reservation(
            reservation.GetReservationRequest(), name="name_value",
        )


def test_delete_reservation(
    transport: str = "grpc", request_type=reservation.DeleteReservationRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.DeleteReservationRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_reservation_from_dict():
    test_delete_reservation(request_type=dict)


@pytest.mark.asyncio
async def test_delete_reservation_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.DeleteReservationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_reservation_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.DeleteReservationRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_reservation), "__call__"
    ) as call:
        call.return_value = None

        client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_reservation_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.DeleteReservationRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_reservation), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_reservation_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_reservation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_reservation_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_reservation(
            reservation.DeleteReservationRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_reservation_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_reservation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_reservation_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_reservation(
            reservation.DeleteReservationRequest(), name="name_value",
        )


def test_update_reservation(
    transport: str = "grpc", request_type=gcbr_reservation.UpdateReservationRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcbr_reservation.Reservation(
            name="name_value", slot_capacity=1391, ignore_idle_slots=True,
        )

        response = client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == gcbr_reservation.UpdateReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcbr_reservation.Reservation)

    assert response.name == "name_value"

    assert response.slot_capacity == 1391

    assert response.ignore_idle_slots is True


def test_update_reservation_from_dict():
    test_update_reservation(request_type=dict)


@pytest.mark.asyncio
async def test_update_reservation_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = gcbr_reservation.UpdateReservationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcbr_reservation.Reservation(
                name="name_value", slot_capacity=1391, ignore_idle_slots=True,
            )
        )

        response = await client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcbr_reservation.Reservation)

    assert response.name == "name_value"

    assert response.slot_capacity == 1391

    assert response.ignore_idle_slots is True


def test_update_reservation_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = gcbr_reservation.UpdateReservationRequest()
    request.reservation.name = "reservation.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_reservation), "__call__"
    ) as call:
        call.return_value = gcbr_reservation.Reservation()

        client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "reservation.name=reservation.name/value",) in kw[
        "metadata"
    ]


@pytest.mark.asyncio
async def test_update_reservation_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = gcbr_reservation.UpdateReservationRequest()
    request.reservation.name = "reservation.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_reservation), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcbr_reservation.Reservation()
        )

        await client.update_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "reservation.name=reservation.name/value",) in kw[
        "metadata"
    ]


def test_update_reservation_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcbr_reservation.Reservation()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_reservation(
            reservation=gcbr_reservation.Reservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].reservation == gcbr_reservation.Reservation(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_reservation_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_reservation(
            gcbr_reservation.UpdateReservationRequest(),
            reservation=gcbr_reservation.Reservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_reservation_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcbr_reservation.Reservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcbr_reservation.Reservation()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_reservation(
            reservation=gcbr_reservation.Reservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].reservation == gcbr_reservation.Reservation(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_reservation_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_reservation(
            gcbr_reservation.UpdateReservationRequest(),
            reservation=gcbr_reservation.Reservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_create_capacity_commitment(
    transport: str = "grpc", request_type=reservation.CreateCapacityCommitmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment(
            name="name_value",
            slot_count=1098,
            plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            state=reservation.CapacityCommitment.State.PENDING,
            renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
        )

        response = client.create_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.CreateCapacityCommitmentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_create_capacity_commitment_from_dict():
    test_create_capacity_commitment(request_type=dict)


@pytest.mark.asyncio
async def test_create_capacity_commitment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.CreateCapacityCommitmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment(
                name="name_value",
                slot_count=1098,
                plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
                state=reservation.CapacityCommitment.State.PENDING,
                renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            )
        )

        response = await client.create_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_create_capacity_commitment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.CreateCapacityCommitmentRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_capacity_commitment), "__call__"
    ) as call:
        call.return_value = reservation.CapacityCommitment()

        client.create_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_capacity_commitment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.CreateCapacityCommitmentRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_capacity_commitment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )

        await client.create_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_capacity_commitment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_capacity_commitment(
            parent="parent_value",
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].capacity_commitment == reservation.CapacityCommitment(
            name="name_value"
        )


def test_create_capacity_commitment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_capacity_commitment(
            reservation.CreateCapacityCommitmentRequest(),
            parent="parent_value",
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_capacity_commitment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_capacity_commitment(
            parent="parent_value",
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].capacity_commitment == reservation.CapacityCommitment(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_create_capacity_commitment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_capacity_commitment(
            reservation.CreateCapacityCommitmentRequest(),
            parent="parent_value",
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
        )


def test_list_capacity_commitments(
    transport: str = "grpc", request_type=reservation.ListCapacityCommitmentsRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListCapacityCommitmentsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.ListCapacityCommitmentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCapacityCommitmentsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_capacity_commitments_from_dict():
    test_list_capacity_commitments(request_type=dict)


@pytest.mark.asyncio
async def test_list_capacity_commitments_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.ListCapacityCommitmentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListCapacityCommitmentsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListCapacityCommitmentsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_capacity_commitments_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.ListCapacityCommitmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_capacity_commitments), "__call__"
    ) as call:
        call.return_value = reservation.ListCapacityCommitmentsResponse()

        client.list_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_capacity_commitments_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.ListCapacityCommitmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_capacity_commitments), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListCapacityCommitmentsResponse()
        )

        await client.list_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_capacity_commitments_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListCapacityCommitmentsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_capacity_commitments(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_capacity_commitments_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_capacity_commitments(
            reservation.ListCapacityCommitmentsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_capacity_commitments_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListCapacityCommitmentsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListCapacityCommitmentsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_capacity_commitments(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_capacity_commitments_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_capacity_commitments(
            reservation.ListCapacityCommitmentsRequest(), parent="parent_value",
        )


def test_list_capacity_commitments_pager():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_capacity_commitments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[], next_page_token="def",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[reservation.CapacityCommitment(),],
                next_page_token="ghi",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_capacity_commitments(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, reservation.CapacityCommitment) for i in results)


def test_list_capacity_commitments_pages():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_capacity_commitments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[], next_page_token="def",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[reservation.CapacityCommitment(),],
                next_page_token="ghi",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_capacity_commitments(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_capacity_commitments_async_pager():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_capacity_commitments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[], next_page_token="def",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[reservation.CapacityCommitment(),],
                next_page_token="ghi",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_capacity_commitments(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, reservation.CapacityCommitment) for i in responses)


@pytest.mark.asyncio
async def test_list_capacity_commitments_async_pages():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_capacity_commitments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[], next_page_token="def",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[reservation.CapacityCommitment(),],
                next_page_token="ghi",
            ),
            reservation.ListCapacityCommitmentsResponse(
                capacity_commitments=[
                    reservation.CapacityCommitment(),
                    reservation.CapacityCommitment(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_capacity_commitments(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_capacity_commitment(
    transport: str = "grpc", request_type=reservation.GetCapacityCommitmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment(
            name="name_value",
            slot_count=1098,
            plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            state=reservation.CapacityCommitment.State.PENDING,
            renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
        )

        response = client.get_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.GetCapacityCommitmentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_get_capacity_commitment_from_dict():
    test_get_capacity_commitment(request_type=dict)


@pytest.mark.asyncio
async def test_get_capacity_commitment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.GetCapacityCommitmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment(
                name="name_value",
                slot_count=1098,
                plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
                state=reservation.CapacityCommitment.State.PENDING,
                renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            )
        )

        response = await client.get_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_get_capacity_commitment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.GetCapacityCommitmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_capacity_commitment), "__call__"
    ) as call:
        call.return_value = reservation.CapacityCommitment()

        client.get_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_capacity_commitment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.GetCapacityCommitmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_capacity_commitment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )

        await client.get_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_capacity_commitment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_capacity_commitment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_capacity_commitment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_capacity_commitment(
            reservation.GetCapacityCommitmentRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_capacity_commitment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_capacity_commitment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_capacity_commitment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_capacity_commitment(
            reservation.GetCapacityCommitmentRequest(), name="name_value",
        )


def test_delete_capacity_commitment(
    transport: str = "grpc", request_type=reservation.DeleteCapacityCommitmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.DeleteCapacityCommitmentRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_capacity_commitment_from_dict():
    test_delete_capacity_commitment(request_type=dict)


@pytest.mark.asyncio
async def test_delete_capacity_commitment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.DeleteCapacityCommitmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_capacity_commitment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.DeleteCapacityCommitmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_capacity_commitment), "__call__"
    ) as call:
        call.return_value = None

        client.delete_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_capacity_commitment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.DeleteCapacityCommitmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_capacity_commitment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_capacity_commitment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_capacity_commitment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_capacity_commitment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_capacity_commitment(
            reservation.DeleteCapacityCommitmentRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_capacity_commitment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_capacity_commitment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_capacity_commitment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_capacity_commitment(
            reservation.DeleteCapacityCommitmentRequest(), name="name_value",
        )


def test_update_capacity_commitment(
    transport: str = "grpc", request_type=reservation.UpdateCapacityCommitmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment(
            name="name_value",
            slot_count=1098,
            plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            state=reservation.CapacityCommitment.State.PENDING,
            renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
        )

        response = client.update_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.UpdateCapacityCommitmentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_update_capacity_commitment_from_dict():
    test_update_capacity_commitment(request_type=dict)


@pytest.mark.asyncio
async def test_update_capacity_commitment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.UpdateCapacityCommitmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment(
                name="name_value",
                slot_count=1098,
                plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
                state=reservation.CapacityCommitment.State.PENDING,
                renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            )
        )

        response = await client.update_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_update_capacity_commitment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.UpdateCapacityCommitmentRequest()
    request.capacity_commitment.name = "capacity_commitment.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_capacity_commitment), "__call__"
    ) as call:
        call.return_value = reservation.CapacityCommitment()

        client.update_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "capacity_commitment.name=capacity_commitment.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_capacity_commitment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.UpdateCapacityCommitmentRequest()
    request.capacity_commitment.name = "capacity_commitment.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_capacity_commitment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )

        await client.update_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "capacity_commitment.name=capacity_commitment.name/value",
    ) in kw["metadata"]


def test_update_capacity_commitment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_capacity_commitment(
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].capacity_commitment == reservation.CapacityCommitment(
            name="name_value"
        )

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_capacity_commitment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_capacity_commitment(
            reservation.UpdateCapacityCommitmentRequest(),
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_capacity_commitment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_capacity_commitment(
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].capacity_commitment == reservation.CapacityCommitment(
            name="name_value"
        )

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_capacity_commitment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_capacity_commitment(
            reservation.UpdateCapacityCommitmentRequest(),
            capacity_commitment=reservation.CapacityCommitment(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_split_capacity_commitment(
    transport: str = "grpc", request_type=reservation.SplitCapacityCommitmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.split_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.SplitCapacityCommitmentResponse()

        response = client.split_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.SplitCapacityCommitmentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.SplitCapacityCommitmentResponse)


def test_split_capacity_commitment_from_dict():
    test_split_capacity_commitment(request_type=dict)


@pytest.mark.asyncio
async def test_split_capacity_commitment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.SplitCapacityCommitmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.split_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.SplitCapacityCommitmentResponse()
        )

        response = await client.split_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.SplitCapacityCommitmentResponse)


def test_split_capacity_commitment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.SplitCapacityCommitmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.split_capacity_commitment), "__call__"
    ) as call:
        call.return_value = reservation.SplitCapacityCommitmentResponse()

        client.split_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_split_capacity_commitment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.SplitCapacityCommitmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.split_capacity_commitment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.SplitCapacityCommitmentResponse()
        )

        await client.split_capacity_commitment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_split_capacity_commitment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.split_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.SplitCapacityCommitmentResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.split_capacity_commitment(
            name="name_value", slot_count=1098,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].slot_count == 1098


def test_split_capacity_commitment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.split_capacity_commitment(
            reservation.SplitCapacityCommitmentRequest(),
            name="name_value",
            slot_count=1098,
        )


@pytest.mark.asyncio
async def test_split_capacity_commitment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.split_capacity_commitment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.SplitCapacityCommitmentResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.SplitCapacityCommitmentResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.split_capacity_commitment(
            name="name_value", slot_count=1098,
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].slot_count == 1098


@pytest.mark.asyncio
async def test_split_capacity_commitment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.split_capacity_commitment(
            reservation.SplitCapacityCommitmentRequest(),
            name="name_value",
            slot_count=1098,
        )


def test_merge_capacity_commitments(
    transport: str = "grpc", request_type=reservation.MergeCapacityCommitmentsRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.merge_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment(
            name="name_value",
            slot_count=1098,
            plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            state=reservation.CapacityCommitment.State.PENDING,
            renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
        )

        response = client.merge_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.MergeCapacityCommitmentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_merge_capacity_commitments_from_dict():
    test_merge_capacity_commitments(request_type=dict)


@pytest.mark.asyncio
async def test_merge_capacity_commitments_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.MergeCapacityCommitmentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.merge_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment(
                name="name_value",
                slot_count=1098,
                plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
                state=reservation.CapacityCommitment.State.PENDING,
                renewal_plan=reservation.CapacityCommitment.CommitmentPlan.FLEX,
            )
        )

        response = await client.merge_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.CapacityCommitment)

    assert response.name == "name_value"

    assert response.slot_count == 1098

    assert response.plan == reservation.CapacityCommitment.CommitmentPlan.FLEX

    assert response.state == reservation.CapacityCommitment.State.PENDING

    assert response.renewal_plan == reservation.CapacityCommitment.CommitmentPlan.FLEX


def test_merge_capacity_commitments_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.MergeCapacityCommitmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.merge_capacity_commitments), "__call__"
    ) as call:
        call.return_value = reservation.CapacityCommitment()

        client.merge_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_merge_capacity_commitments_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.MergeCapacityCommitmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.merge_capacity_commitments), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )

        await client.merge_capacity_commitments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_merge_capacity_commitments_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.merge_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.merge_capacity_commitments(
            parent="parent_value",
            capacity_commitment_ids=["capacity_commitment_ids_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].capacity_commitment_ids == ["capacity_commitment_ids_value"]


def test_merge_capacity_commitments_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.merge_capacity_commitments(
            reservation.MergeCapacityCommitmentsRequest(),
            parent="parent_value",
            capacity_commitment_ids=["capacity_commitment_ids_value"],
        )


@pytest.mark.asyncio
async def test_merge_capacity_commitments_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.merge_capacity_commitments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.CapacityCommitment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.CapacityCommitment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.merge_capacity_commitments(
            parent="parent_value",
            capacity_commitment_ids=["capacity_commitment_ids_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].capacity_commitment_ids == ["capacity_commitment_ids_value"]


@pytest.mark.asyncio
async def test_merge_capacity_commitments_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.merge_capacity_commitments(
            reservation.MergeCapacityCommitmentsRequest(),
            parent="parent_value",
            capacity_commitment_ids=["capacity_commitment_ids_value"],
        )


def test_create_assignment(
    transport: str = "grpc", request_type=reservation.CreateAssignmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Assignment(
            name="name_value",
            assignee="assignee_value",
            job_type=reservation.Assignment.JobType.PIPELINE,
            state=reservation.Assignment.State.PENDING,
        )

        response = client.create_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.CreateAssignmentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.Assignment)

    assert response.name == "name_value"

    assert response.assignee == "assignee_value"

    assert response.job_type == reservation.Assignment.JobType.PIPELINE

    assert response.state == reservation.Assignment.State.PENDING


def test_create_assignment_from_dict():
    test_create_assignment(request_type=dict)


@pytest.mark.asyncio
async def test_create_assignment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.CreateAssignmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Assignment(
                name="name_value",
                assignee="assignee_value",
                job_type=reservation.Assignment.JobType.PIPELINE,
                state=reservation.Assignment.State.PENDING,
            )
        )

        response = await client.create_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.Assignment)

    assert response.name == "name_value"

    assert response.assignee == "assignee_value"

    assert response.job_type == reservation.Assignment.JobType.PIPELINE

    assert response.state == reservation.Assignment.State.PENDING


def test_create_assignment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.CreateAssignmentRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_assignment), "__call__"
    ) as call:
        call.return_value = reservation.Assignment()

        client.create_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_create_assignment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.CreateAssignmentRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_assignment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Assignment()
        )

        await client.create_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_create_assignment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Assignment()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_assignment(
            parent="parent_value", assignment=reservation.Assignment(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].assignment == reservation.Assignment(name="name_value")


def test_create_assignment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_assignment(
            reservation.CreateAssignmentRequest(),
            parent="parent_value",
            assignment=reservation.Assignment(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_assignment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.create_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Assignment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Assignment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_assignment(
            parent="parent_value", assignment=reservation.Assignment(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].assignment == reservation.Assignment(name="name_value")


@pytest.mark.asyncio
async def test_create_assignment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_assignment(
            reservation.CreateAssignmentRequest(),
            parent="parent_value",
            assignment=reservation.Assignment(name="name_value"),
        )


def test_list_assignments(
    transport: str = "grpc", request_type=reservation.ListAssignmentsRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListAssignmentsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.ListAssignmentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAssignmentsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_assignments_from_dict():
    test_list_assignments(request_type=dict)


@pytest.mark.asyncio
async def test_list_assignments_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.ListAssignmentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListAssignmentsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAssignmentsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_assignments_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.ListAssignmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_assignments), "__call__"
    ) as call:
        call.return_value = reservation.ListAssignmentsResponse()

        client.list_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_assignments_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.ListAssignmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assignments), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListAssignmentsResponse()
        )

        await client.list_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_assignments_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListAssignmentsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_assignments(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


def test_list_assignments_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_assignments(
            reservation.ListAssignmentsRequest(), parent="parent_value",
        )


@pytest.mark.asyncio
async def test_list_assignments_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.ListAssignmentsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.ListAssignmentsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_assignments(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"


@pytest.mark.asyncio
async def test_list_assignments_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_assignments(
            reservation.ListAssignmentsRequest(), parent="parent_value",
        )


def test_list_assignments_pager():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_assignments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListAssignmentsResponse(assignments=[], next_page_token="def",),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.list_assignments(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, reservation.Assignment) for i in results)


def test_list_assignments_pages():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_assignments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListAssignmentsResponse(assignments=[], next_page_token="def",),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_assignments(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_assignments_async_pager():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assignments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListAssignmentsResponse(assignments=[], next_page_token="def",),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )
        async_pager = await client.list_assignments(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, reservation.Assignment) for i in responses)


@pytest.mark.asyncio
async def test_list_assignments_async_pages():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.list_assignments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.ListAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.ListAssignmentsResponse(assignments=[], next_page_token="def",),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.ListAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_assignments(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_delete_assignment(
    transport: str = "grpc", request_type=reservation.DeleteAssignmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.delete_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.DeleteAssignmentRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_assignment_from_dict():
    test_delete_assignment(request_type=dict)


@pytest.mark.asyncio
async def test_delete_assignment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.DeleteAssignmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        response = await client.delete_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_assignment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.DeleteAssignmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_assignment), "__call__"
    ) as call:
        call.return_value = None

        client.delete_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_assignment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.DeleteAssignmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_assignment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)

        await client.delete_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_delete_assignment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_assignment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_delete_assignment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_assignment(
            reservation.DeleteAssignmentRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_delete_assignment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.delete_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_assignment(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_delete_assignment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_assignment(
            reservation.DeleteAssignmentRequest(), name="name_value",
        )


def test_search_assignments(
    transport: str = "grpc", request_type=reservation.SearchAssignmentsRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.SearchAssignmentsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.search_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.SearchAssignmentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchAssignmentsPager)

    assert response.next_page_token == "next_page_token_value"


def test_search_assignments_from_dict():
    test_search_assignments(request_type=dict)


@pytest.mark.asyncio
async def test_search_assignments_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.SearchAssignmentsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.SearchAssignmentsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.search_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchAssignmentsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


def test_search_assignments_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.SearchAssignmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_assignments), "__call__"
    ) as call:
        call.return_value = reservation.SearchAssignmentsResponse()

        client.search_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_assignments_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.SearchAssignmentsRequest()
    request.parent = "parent/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_assignments), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.SearchAssignmentsResponse()
        )

        await client.search_assignments(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_search_assignments_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.SearchAssignmentsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.search_assignments(
            parent="parent_value", query="query_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].query == "query_value"


def test_search_assignments_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.search_assignments(
            reservation.SearchAssignmentsRequest(),
            parent="parent_value",
            query="query_value",
        )


@pytest.mark.asyncio
async def test_search_assignments_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_assignments), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.SearchAssignmentsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.SearchAssignmentsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.search_assignments(
            parent="parent_value", query="query_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].parent == "parent_value"

        assert args[0].query == "query_value"


@pytest.mark.asyncio
async def test_search_assignments_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.search_assignments(
            reservation.SearchAssignmentsRequest(),
            parent="parent_value",
            query="query_value",
        )


def test_search_assignments_pager():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_assignments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.SearchAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[], next_page_token="def",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.search_assignments(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, reservation.Assignment) for i in results)


def test_search_assignments_pages():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.search_assignments), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.SearchAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[], next_page_token="def",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )
        pages = list(client.search_assignments(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_search_assignments_async_pager():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_assignments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.SearchAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[], next_page_token="def",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )
        async_pager = await client.search_assignments(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, reservation.Assignment) for i in responses)


@pytest.mark.asyncio
async def test_search_assignments_async_pages():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.search_assignments),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            reservation.SearchAssignmentsResponse(
                assignments=[
                    reservation.Assignment(),
                    reservation.Assignment(),
                    reservation.Assignment(),
                ],
                next_page_token="abc",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[], next_page_token="def",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(),], next_page_token="ghi",
            ),
            reservation.SearchAssignmentsResponse(
                assignments=[reservation.Assignment(), reservation.Assignment(),],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.search_assignments(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_move_assignment(
    transport: str = "grpc", request_type=reservation.MoveAssignmentRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.move_assignment), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Assignment(
            name="name_value",
            assignee="assignee_value",
            job_type=reservation.Assignment.JobType.PIPELINE,
            state=reservation.Assignment.State.PENDING,
        )

        response = client.move_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.MoveAssignmentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.Assignment)

    assert response.name == "name_value"

    assert response.assignee == "assignee_value"

    assert response.job_type == reservation.Assignment.JobType.PIPELINE

    assert response.state == reservation.Assignment.State.PENDING


def test_move_assignment_from_dict():
    test_move_assignment(request_type=dict)


@pytest.mark.asyncio
async def test_move_assignment_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.MoveAssignmentRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.move_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Assignment(
                name="name_value",
                assignee="assignee_value",
                job_type=reservation.Assignment.JobType.PIPELINE,
                state=reservation.Assignment.State.PENDING,
            )
        )

        response = await client.move_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.Assignment)

    assert response.name == "name_value"

    assert response.assignee == "assignee_value"

    assert response.job_type == reservation.Assignment.JobType.PIPELINE

    assert response.state == reservation.Assignment.State.PENDING


def test_move_assignment_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.MoveAssignmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.move_assignment), "__call__") as call:
        call.return_value = reservation.Assignment()

        client.move_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_move_assignment_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.MoveAssignmentRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.move_assignment), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Assignment()
        )

        await client.move_assignment(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_move_assignment_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.move_assignment), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Assignment()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.move_assignment(
            name="name_value", destination_id="destination_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].destination_id == "destination_id_value"


def test_move_assignment_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.move_assignment(
            reservation.MoveAssignmentRequest(),
            name="name_value",
            destination_id="destination_id_value",
        )


@pytest.mark.asyncio
async def test_move_assignment_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.move_assignment), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.Assignment()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.Assignment()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.move_assignment(
            name="name_value", destination_id="destination_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].destination_id == "destination_id_value"


@pytest.mark.asyncio
async def test_move_assignment_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.move_assignment(
            reservation.MoveAssignmentRequest(),
            name="name_value",
            destination_id="destination_id_value",
        )


def test_get_bi_reservation(
    transport: str = "grpc", request_type=reservation.GetBiReservationRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.BiReservation(name="name_value", size=443,)

        response = client.get_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.GetBiReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.BiReservation)

    assert response.name == "name_value"

    assert response.size == 443


def test_get_bi_reservation_from_dict():
    test_get_bi_reservation(request_type=dict)


@pytest.mark.asyncio
async def test_get_bi_reservation_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.GetBiReservationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.BiReservation(name="name_value", size=443,)
        )

        response = await client.get_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.BiReservation)

    assert response.name == "name_value"

    assert response.size == 443


def test_get_bi_reservation_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.GetBiReservationRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_bi_reservation), "__call__"
    ) as call:
        call.return_value = reservation.BiReservation()

        client.get_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_bi_reservation_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.GetBiReservationRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_bi_reservation), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.BiReservation()
        )

        await client.get_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_bi_reservation_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.BiReservation()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_bi_reservation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_bi_reservation_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_bi_reservation(
            reservation.GetBiReservationRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_bi_reservation_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.get_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.BiReservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.BiReservation()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_bi_reservation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_bi_reservation_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_bi_reservation(
            reservation.GetBiReservationRequest(), name="name_value",
        )


def test_update_bi_reservation(
    transport: str = "grpc", request_type=reservation.UpdateBiReservationRequest
):
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.BiReservation(name="name_value", size=443,)

        response = client.update_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == reservation.UpdateBiReservationRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.BiReservation)

    assert response.name == "name_value"

    assert response.size == 443


def test_update_bi_reservation_from_dict():
    test_update_bi_reservation(request_type=dict)


@pytest.mark.asyncio
async def test_update_bi_reservation_async(transport: str = "grpc_asyncio"):
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = reservation.UpdateBiReservationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.BiReservation(name="name_value", size=443,)
        )

        response = await client.update_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, reservation.BiReservation)

    assert response.name == "name_value"

    assert response.size == 443


def test_update_bi_reservation_field_headers():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.UpdateBiReservationRequest()
    request.bi_reservation.name = "bi_reservation.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_bi_reservation), "__call__"
    ) as call:
        call.return_value = reservation.BiReservation()

        client.update_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "bi_reservation.name=bi_reservation.name/value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_bi_reservation_field_headers_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = reservation.UpdateBiReservationRequest()
    request.bi_reservation.name = "bi_reservation.name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_bi_reservation), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.BiReservation()
        )

        await client.update_bi_reservation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "bi_reservation.name=bi_reservation.name/value",
    ) in kw["metadata"]


def test_update_bi_reservation_flattened():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.update_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.BiReservation()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_bi_reservation(
            bi_reservation=reservation.BiReservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].bi_reservation == reservation.BiReservation(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_bi_reservation_flattened_error():
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_bi_reservation(
            reservation.UpdateBiReservationRequest(),
            bi_reservation=reservation.BiReservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


@pytest.mark.asyncio
async def test_update_bi_reservation_flattened_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._client._transport.update_bi_reservation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = reservation.BiReservation()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            reservation.BiReservation()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_bi_reservation(
            bi_reservation=reservation.BiReservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].bi_reservation == reservation.BiReservation(name="name_value")

        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


@pytest.mark.asyncio
async def test_update_bi_reservation_flattened_error_async():
    client = ReservationServiceAsyncClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_bi_reservation(
            reservation.UpdateBiReservationRequest(),
            bi_reservation=reservation.BiReservation(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ReservationServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ReservationServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.ReservationServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ReservationServiceClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.ReservationServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ReservationServiceClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ReservationServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = ReservationServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ReservationServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.ReservationServiceGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = ReservationServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.ReservationServiceGrpcTransport,)


def test_reservation_service_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.ReservationServiceTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_reservation_service_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.bigquery.reservation_v1.services.reservation_service.transports.ReservationServiceTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.ReservationServiceTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_reservation",
        "list_reservations",
        "get_reservation",
        "delete_reservation",
        "update_reservation",
        "create_capacity_commitment",
        "list_capacity_commitments",
        "get_capacity_commitment",
        "delete_capacity_commitment",
        "update_capacity_commitment",
        "split_capacity_commitment",
        "merge_capacity_commitments",
        "create_assignment",
        "list_assignments",
        "delete_assignment",
        "search_assignments",
        "move_assignment",
        "get_bi_reservation",
        "update_bi_reservation",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_reservation_service_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.bigquery.reservation_v1.services.reservation_service.transports.ReservationServiceTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.ReservationServiceTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=(
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            quota_project_id="octopus",
        )


def test_reservation_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        ReservationServiceClient()
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            quota_project_id=None,
        )


def test_reservation_service_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.ReservationServiceGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=(
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            quota_project_id="octopus",
        )


def test_reservation_service_host_no_port():
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="bigqueryreservation.googleapis.com"
        ),
    )
    assert client._transport._host == "bigqueryreservation.googleapis.com:443"


def test_reservation_service_host_with_port():
    client = ReservationServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="bigqueryreservation.googleapis.com:8000"
        ),
    )
    assert client._transport._host == "bigqueryreservation.googleapis.com:8000"


def test_reservation_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.ReservationServiceGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


def test_reservation_service_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that if channel is provided, mtls endpoint and client_cert_source
    # won't be used.
    callback = mock.MagicMock()
    transport = transports.ReservationServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=callback,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert not callback.called


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_reservation_service_grpc_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.ReservationServiceGrpcTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=(
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/cloud-platform",
        ),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@mock.patch("grpc.ssl_channel_credentials", autospec=True)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_reservation_service_grpc_asyncio_transport_channel_mtls_with_client_cert_source(
    grpc_create_channel, grpc_ssl_channel_cred
):
    # Check that if channel is None, but api_mtls_endpoint and client_cert_source
    # are provided, then a mTLS channel will be created.
    mock_cred = mock.Mock()

    mock_ssl_cred = mock.Mock()
    grpc_ssl_channel_cred.return_value = mock_ssl_cred

    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    transport = transports.ReservationServiceGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        credentials=mock_cred,
        api_mtls_endpoint="mtls.squid.clam.whelk",
        client_cert_source=client_cert_source_callback,
    )
    grpc_ssl_channel_cred.assert_called_once_with(
        certificate_chain=b"cert bytes", private_key=b"key bytes"
    )
    grpc_create_channel.assert_called_once_with(
        "mtls.squid.clam.whelk:443",
        credentials=mock_cred,
        credentials_file=None,
        scopes=(
            "https://www.googleapis.com/auth/bigquery",
            "https://www.googleapis.com/auth/cloud-platform",
        ),
        ssl_credentials=mock_ssl_cred,
        quota_project_id=None,
    )
    assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers.create_channel", autospec=True)
def test_reservation_service_grpc_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.ReservationServiceGrpcTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


@pytest.mark.parametrize(
    "api_mtls_endpoint", ["mtls.squid.clam.whelk", "mtls.squid.clam.whelk:443"]
)
@mock.patch("google.api_core.grpc_helpers_async.create_channel", autospec=True)
def test_reservation_service_grpc_asyncio_transport_channel_mtls_with_adc(
    grpc_create_channel, api_mtls_endpoint
):
    # Check that if channel and client_cert_source are None, but api_mtls_endpoint
    # is provided, then a mTLS channel will be created with SSL ADC.
    mock_grpc_channel = mock.Mock()
    grpc_create_channel.return_value = mock_grpc_channel

    # Mock google.auth.transport.grpc.SslCredentials class.
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        mock_cred = mock.Mock()
        transport = transports.ReservationServiceGrpcAsyncIOTransport(
            host="squid.clam.whelk",
            credentials=mock_cred,
            api_mtls_endpoint=api_mtls_endpoint,
            client_cert_source=None,
        )
        grpc_create_channel.assert_called_once_with(
            "mtls.squid.clam.whelk:443",
            credentials=mock_cred,
            credentials_file=None,
            scopes=(
                "https://www.googleapis.com/auth/bigquery",
                "https://www.googleapis.com/auth/cloud-platform",
            ),
            ssl_credentials=mock_ssl_cred,
            quota_project_id=None,
        )
        assert transport.grpc_channel == mock_grpc_channel


def test_assignment_path():
    project = "squid"
    location = "clam"
    reservation = "whelk"
    assignment = "octopus"

    expected = "projects/{project}/locations/{location}/reservations/{reservation}/assignments/{assignment}".format(
        project=project,
        location=location,
        reservation=reservation,
        assignment=assignment,
    )
    actual = ReservationServiceClient.assignment_path(
        project, location, reservation, assignment
    )
    assert expected == actual


def test_parse_assignment_path():
    expected = {
        "project": "oyster",
        "location": "nudibranch",
        "reservation": "cuttlefish",
        "assignment": "mussel",
    }
    path = ReservationServiceClient.assignment_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationServiceClient.parse_assignment_path(path)
    assert expected == actual


def test_capacity_commitment_path():
    project = "squid"
    location = "clam"
    capacity_commitment = "whelk"

    expected = "projects/{project}/locations/{location}/capacityCommitments/{capacity_commitment}".format(
        project=project, location=location, capacity_commitment=capacity_commitment,
    )
    actual = ReservationServiceClient.capacity_commitment_path(
        project, location, capacity_commitment
    )
    assert expected == actual


def test_parse_capacity_commitment_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "capacity_commitment": "nudibranch",
    }
    path = ReservationServiceClient.capacity_commitment_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationServiceClient.parse_capacity_commitment_path(path)
    assert expected == actual


def test_reservation_path():
    project = "squid"
    location = "clam"
    reservation = "whelk"

    expected = "projects/{project}/locations/{location}/reservations/{reservation}".format(
        project=project, location=location, reservation=reservation,
    )
    actual = ReservationServiceClient.reservation_path(project, location, reservation)
    assert expected == actual


def test_parse_reservation_path():
    expected = {
        "project": "octopus",
        "location": "oyster",
        "reservation": "nudibranch",
    }
    path = ReservationServiceClient.reservation_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationServiceClient.parse_reservation_path(path)
    assert expected == actual


def test_bi_reservation_path():
    project = "squid"
    location = "clam"

    expected = "projects/{project}/locations/{location}/bireservation".format(
        project=project, location=location,
    )
    actual = ReservationServiceClient.bi_reservation_path(project, location)
    assert expected == actual


def test_parse_bi_reservation_path():
    expected = {
        "project": "whelk",
        "location": "octopus",
    }
    path = ReservationServiceClient.bi_reservation_path(**expected)

    # Check that the path construction is reversible.
    actual = ReservationServiceClient.parse_bi_reservation_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.ReservationServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        client = ReservationServiceClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.ReservationServiceTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = ReservationServiceClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

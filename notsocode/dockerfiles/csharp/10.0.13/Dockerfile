ARG BASE_IMAGE=base-buster
FROM $BASE_IMAGE

RUN apt update -y && apt install -y libicu72

WORKDIR /tmp
RUN mkdir -p /usr/share/dotnet && wget "https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.402/dotnet-sdk-10.0.402-linux-x64.tar.gz" -q -O dotnet.tar.gz && \
	tar xzf dotnet.tar.gz -C /usr/share/dotnet && rm dotnet.tar.gz && ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet

ENV DOTNET_CLI_TELEMETRY_OPTOUT=1
ENV DOTNET_NOLOGO=1
ENV DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
ENV DOTNET_GENERATE_ASPNET_CERTIFICATE=false
# `dotnet run file.cs` spends most of its time in msbuild, calling roslyn directly is ~4x faster;
# the usings are the ones the sdk adds implicitly for a console app
RUN printf '#!/bin/sh\nexec dotnet %s "$@"\n' "$(ls /usr/share/dotnet/sdk/*/Roslyn/bincore/csc.dll)" > /usr/local/bin/csc && chmod +x /usr/local/bin/csc
RUN mkdir -p /opt/csharp && \
	printf 'global using System;\nglobal using System.Collections.Generic;\nglobal using System.IO;\nglobal using System.Linq;\nglobal using System.Net.Http;\nglobal using System.Threading;\nglobal using System.Threading.Tasks;\n' > /opt/csharp/usings.cs && \
	{ printf -- '-nologo\n-langversion:latest\n-nullable:enable\n-unsafe+\n-optimize+\n'; \
		for dll in /usr/share/dotnet/packs/Microsoft.NETCore.App.Ref/*/ref/net10.0/*.dll; do echo "-r:$dll"; done; \
		echo /opt/csharp/usings.cs; } > /opt/csharp/csc.rsp && \
	printf '{"runtimeOptions":{"tfm":"net10.0","framework":{"name":"Microsoft.NETCore.App","version":"%s"}}}' \
		"$(ls /usr/share/dotnet/shared/Microsoft.NETCore.App/)" > /opt/csharp/binary.runtimeconfig.json

ENV COMMAND_COMPILE='csc @/opt/csharp/csc.rsp -out:./binary.dll $SCRIPT && cp /opt/csharp/binary.runtimeconfig.json ./'
ENV COMMAND='dotnet ./binary.dll'

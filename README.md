[![PyPI](https://img.shields.io/pypi/v/jinjafx-server.svg)](https://pypi.python.org/pypi/jinjafx-server/)
![Python](https://img.shields.io/badge/python-≥&nbsp;3.6-brightgreen)
[<img src="https://img.shields.io/badge/url-https%3A%2F%2Fjinjafx.io-blue" align="right">](https://jinjafx.io)
&nbsp;
<h1 align="center">JinjaFx Server - Jinja2 Templating Tool</h1>

JinjaFx Server is a lightweight web server that provides a Web UI to JinjaFx. It is a separate Python module which imports the "jinjafx" module to generate outputs from a web interface - it does require the "requests" module which isn't in the base install. Usage instructions are provided below, although it is considered an additional component and not part of the base JinjaFx tool, although it is probably a much easier way to use it.

### Installation

```
python3 -m pip install --upgrade --user jinjafx-server
```

### JinjaFx Server Usage

Once JinjaFx Server has been started with the `-s` argument then point your web browser at http://localhost:8080 and you will be presented with a web page that allows you to specify `data.csv`, `template.j2` and `vars.yml` and then generate outputs. If you click on "Export" then it will present you with an output that can be pasted back into any pane of JinjaFx to restore the values.

```
 jinjafx_server -s [-l <address>] [-p <port>] [-r <repository> | -s3 <aws s3 url>] [-rl <rate/limit>] [-tl <time limit>] [-ml <memory limit>]
   -s                          - start the JinjaFx Server
   -l <address>                - specify a listen address (default is '127.0.0.1')
   -p <port>                   - specify a listen port (default is 8080)
   -r <repository>             - specify a local repository directory (allows 'Get Link')
   -s3 <aws s3 url>            - specify a repository using aws s3 buckets (allows 'Get Link')
   -rl <rate/limit>            - specify a rate limit (i.e. '5/30s' for 5 requests in 30 seconds)
   -tl <time limit>            - specify a time limit per request (seconds)
   -ml <memory limit>          - specify a global memory limit (megabytes < total) 
   -v                          - log all HTTP requests

 Environment Variables:
   AWS_ACCESS_KEY              - specify an aws access key to authenticate for '-s3'
   AWS_SECRET_KEY              - specify an aws secret key to authenticate for '-s3'
```

For health checking purposes, if you specify the URL `/ping` then you should get an "OK" response if the JinaFx Server is up and working (these requests are omitted from the logs). The preferred method of running the JinjaFx Server is with HAProxy in front of it as it supports TLS termination and HTTP/2 - please see the [/docker](https://github.com/cmason3/jinjafx_server/blob/main/docker) directory for more information.

The "-r" or "-s3" arguments (mutually exclusive) allow you to specify a repository ("-r" is a local directory and "-s3" is an AWS S3 URL) that will be used to store DataTemplates on the server via the "Get Link" and "Update Link" buttons. The generated link is guaranteed to be unique and a different link will be created every time - version 1.3.0 changed the behaviour, where previously the same link was always generated for the same DataTemplate, but this made it difficult to update DataTemplates without the link changing as it was basically a cryptographic hash of your DataTemplate. If you use an AWS S3 bucket then you will also need to provide some credentials via the two environment variables which has read and write permissions to the S3 URL.

The "-rl" argument is used to provide an optional rate limit of the source IP - the "rate" is how many requests are permitted and the "limit" is the interval in which those requests are permitted - it can be specified in "s", "m" or "h" (e.g. "5/30s", "10/1m" or "30/1h").

### Shortcut Keys

As well as supporting the standard CodeMirror shortcut keys for the "data.csv", "vars.yml" and "template.j2" panes, it also supports the following custom shortcut keys:

- F11 / Cmd-Enter - Toggle Fullscreen

- Ctrl-G / Cmd-G - Generate

- Ctrl-S / Cmd-S - Update Link

- Ctrl-F / Cmd-F - Find

### DataSets

The DataSet feature allows you to include multiple different "data.csv" and "vars.yml" contents while maintaining the same "template.j2". This is to support scenarios where you have different DataSets for your Live vs your Test environments, but the template should be the same. There are no limits on the number of different DataSets that can be added to a single DataTemplate (the name must start with a letter and only contain alphanumerical, "-", " " or "_" characters). When you click "Generate" it will use the currently active DataSet to generate the output - clicking on the name of the current DataSet (by default there is a single "Default" DataSet) allows you to switch between the different DataSets.

### Output Formats

JinjaFx Server supports the ability to use "output" tags to create different outputs with different names like JinjaFx, but it also allows you to optionally specify how you want the output to be rendered. By default, the output is rendered as "text" but you also have the option to specify "html" and "markdown" (for GitHub Flavoured Markdown), which will result in the output being rendered appropriately, e.g:

```jinja2
<output:html "index.html">
<html>
...
</html>
</output>

<output:markdown "index.md">
- Item 1
- Item 2
- Item 3
</output>
```

### Ansible Vault

JinjaFx Server supports the ability to perform Ansible Vault encryption of strings from within the browser using client side JavaScript. By clicking on the padlock it will prompt you for your string and the password to use which you can then use within `vars.yml`. JinjaFx doesn't support the ability to use different passwords for different strings within the same DataTemplate so it is important that all vaulted strings are using the same password within the same DataTemplate.

### JinjaFx Input

There might be some situations where you want inputs to be provided during the generation of the template which are not known beforehand. JinjaFx supports the ability to prompt the user for input using the `jinjafx_input` variable which can be specified in `vars.yml`. The following example demonstrates how we can prompt the user for two inputs ("Name" and "Age") before the template is generated:

```yaml
---
jinjafx_input:
  prompt:
    name: "Name"
    age: "Age"
```

These inputs can then be referenced in your template using `{{ jinjafx_input.name }}` or `{{ jinjafx_input['age'] }}` - the variable name is the field name and the prompt text is the value. However, there might be some situations where you want a certain pattern to be followed or where an input is mandatory, and this is where the advanced syntax comes into play (you can mix and match syntax for different fields):

```yaml
---
jinjafx_input:
  prompt:
    name:
      text: "Name"
      required: True
    age:
      text: "Age"
      required: True
      pattern: "[1-9]+[0-9]*"
```

Under the field the `text` key is always mandatory, but the following optional keys are also valid:

- `required` - can be True or False (default is False)

- `pattern` - a regular expression that the input value must match

- `type` - if set to "password" then echo is turned off - used for inputting sensitive values

In addition to the above prompt syntax, we also support the ability to specify a custom html input form to provide greater flexibility. As JinjaFx is built on Bootstrap 5, it uses the <a href="https://getbootstrap.com/docs/5.1/components/modal/#modal-components">Bootstrap 5 Modal</a> syntax to specify what is contained in the body of your modal form. Bootstrap works on a row and column grid with each row comprising of 12 columns - you use the various "col-n" classes to specify how wide each element is.

You can specify a custom input form using the `body` variable under `jinjafx_input` within your "vars.yml" - if this exists then whatever you have in `prompt` is ignored.

```yaml
---
jinjafx_input:
  body: |2
    <div class="row">
      <div class="col-6">
        <label for="name" class="col-form-label">Name</label>
        <input id="name" class="form-control" data-var="name" required>
      </div>
      <div class="col-6">
        <label for="gender" class="col-form-label">Gender</label>
        <select id="gender" class="form-control" data-var="gender">
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select>
      </div>
    </div>
```

You can also specify an optional `size` attribute alongside the `body` attribute which sets the width of the modal using the pre-defined Bootstrap sizes (i.e. "sm", "lg" and "xl"). The input form supports full native HTML validation using `required` and `pattern` attributes. The values which are input are then mapped to Jinja2 variables using the `data-var` custom attribute (e.g. `data-var="name"` would map to `jinjafx_input['name']` or `jinjafx_input.name`):

```jinja2
Name: {{ jinjafx_input['name'] }}
Gender: {{ jinjafx_input['gender'] }}
```

If you specify the same `data-var` value more than once in the input form then the variable will be converted into a list using the values in the order they appear in the form.

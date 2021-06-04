<!-- PROJECT SHIELDS -->
<!--
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![Build][build-shield]][build-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/EOEPCA/eoepca">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">EOEPCA Helm Charts Development Repository</h3>

  <p align="center">
    EOEPCA Reference Implementation - Helm Charts Development Repository
    <br />
    <a href="https://eoepca.github.io/helm-charts-dev/"><strong>Repository Index »</strong></a>
    <br />
    <a href="https://github.com/EOEPCA/helm-charts">View Demo</a>
    ·
    <a href="https://github.com/EOEPCA/helm-charts/issues">Report Bug</a>
    ·
    <a href="https://github.com/EOEPCA/helm-charts/issues">Request Feature</a>
  </p>
</p>


<!-- TABLE OF CONTENTS -->
## Table of Contents

- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
- [Development process](#development-process)
- [Issues](#issues)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)


<!-- GETTING STARTED -->
## Getting Started

To use the eoepca helm chart repository, just add the repo update it an install packages as usual
```
$ helm repo add eoepca-dev https://eoepca.github.io/helm-charts-dev/
$ helm repo update
$ helm install test eoepca-dev/cheese
```

## Development process
This helm chart repository is used following the example at https://helm.sh/docs/topics/chart_repository/#github-pages-example it uses the chart releaser (cr) https://helm.sh/docs/howto/chart_releaser_action/ in a github action to create the packages and update the repository index automatically.
When a a change is detected in one of the charts at charts/ folder it creates a new package and add it to the index, this means that every time a change is made, the version needs to be increased.

### Steps to develop
- Point your test enviroment to https://eoepca.github.io/helm-charts-dev/
- Create your own branch to introduce new changes
- Increase the version of the package
- Merge it with *develop* branch, this will create a new package/release on https://eoepca.github.io/helm-charts-dev/ that your test enviroment can install
- If the test is succesfull and you want to release the package/release to production merge it on the *main* branch, this will trigger and automated action and it will be released in https://eoepca.github.io/helm-charts/

<!-- ISSUES -->
## Issues

See the [open issues](https://github.com/EOEPCA/helm-charts/issues) for a list of proposed features (and known issues).

<!-- LICENSE -->
## License

The EOEPCA SYSTEM is distributed under the European Space Agency - ESA Software Community Licence Permissive – v2.4. See `LICENSE` for more information.

Building-blocks and their sub-components are individually licensed. See their respective source repositories for details.


<!-- CONTACT -->
## Contact

Project Link: [Project Home (https://eoepca.github.io/)](https://eoepca.github.io/)


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* README.md is based on [this template](https://github.com/othneildrew/Best-README-Template) by [Othneil Drew](https://github.com/othneildrew).


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/EOEPCA/eoepca.svg?style=flat-square
[contributors-url]: https://github.com/EOEPCA/eoepca/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/EOEPCA/eoepca.svg?style=flat-square
[forks-url]: https://github.com/EOEPCA/eoepca/network/members
[stars-shield]: https://img.shields.io/github/stars/EOEPCA/eoepca.svg?style=flat-square
[stars-url]: https://github.com/EOEPCA/eoepca/stargazers
[issues-shield]: https://img.shields.io/github/issues/EOEPCA/eoepca.svg?style=flat-square
[issues-url]: https://github.com/EOEPCA/eoepca/issues
[license-shield]: https://img.shields.io/github/license/EOEPCA/eoepca.svg?style=flat-square
[license-url]: https://github.com/EOEPCA/eoepca/blob/master/LICENSE
[build-shield]: https://www.travis-ci.com/EOEPCA/eoepca.svg?branch=master
[build-url]: https://travis-ci.com/github/EOEPCA/eoepca
[product-screenshot]: images/screenshot.png

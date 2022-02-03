import React, { Component } from 'react'
import axios from 'axios'
import { Badge, Button, Card, CardDeck, CardTitle, CardBody, CardHeader, CardText, Col, Form, FormGroup, Input, Label} from 'reactstrap'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Link, Redirect } from 'react-router-dom'
import TagsTable from './tagstable'
import FilesTable from './filestable'
import ReactPaginate from 'react-paginate';

export default class Files extends Component {
  constructor (props) {
    super(props)
    this.state = {
      isLoading: true,
      files: [],
      pageCount: 1,
      total: 0,
      tags: [],
      selectedTags: [],
    }
    this.utils = new Utils()
    this.listFiles = this.listFiles.bind(this)
    this.listTags = this.listTags.bind(this)
    this.filterTags = this.filterTags.bind(this)
  }


  componentDidMount () {
    this.listFiles()
    this.listTags()
  }

  filterTags(event){
    let updateList
    if (event.target.checked){
      updateList = [...this.state.selectedTags, event.target.value]
    } else {
      updateList = [...this.state.selectedTags].splice(checked.indexOf(event.target.value), 1)
    }
    this.setState({
      selectedTags: updateList
    }, () => {
      this.listTags();
    })
  }

  listFiles(offset=0) {

    let requestUrl = '/api/list'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c }), params:{offset: offset, limit: this.props.config.perPage, tags: this.state.selectedTags}})
      .then(response => {
        this.setState({
          isLoading: false,
          files: response.data.files,
          pageCount: Math.ceil(response.data.total / this.props.config.perPage),
          total: response.data.total
        })
      })
      .catch(error => {
        console.log(error.response)
        this.setState({
            error: true,
            errorCode: error.response.status,
            errorMessage: error.response.statusText,
        })
      })
  }

  listTags() {
    let requestUrl = '/api/tag/list'
    axios.get(requestUrl, { baseURL: this.props.config.proxyPath, cancelToken: new axios.CancelToken((c) => { this.cancelRequest = c })})
      .then(response => {
        this.setState({
          tags: response.data.tags,
        })
      })
      .catch(error => {
        console.log(error.response)
        this.setState({
            error: true,
            errorCode: error.response.status,
            errorMessage: error.response.statusText,
        })
      })
  }

  render () {

    if (this.state.error) {
        return (
            <div className="container">
            <h2>Error <i>{this.state.errorCode}</i> fetching files: <i>{this.state.errorMessage}</i></h2>
            </div>
        )
    }

    return (
        <div className="container">
        <TagsTable config={this.props.config} tags={this.state.tags} selectedTags={this.state.selectedTags} updateList={this.filterTags}/>
        <FilesTable config={this.props.config} files={this.state.files} total={this.state.total} getData={this.listFiles} pageCount={this.state.pageCount}/>
        </div>
    )
  }
}

Files.propTypes = {
  config: PropTypes.object,
}

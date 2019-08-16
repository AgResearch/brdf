--
-- Name: hiseqsamplesheetfact_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY hiseqsamplesheetfact
    ADD CONSTRAINT hiseqsamplesheetfact_pkey PRIMARY KEY (factid);


--
-- Name: hiseqsamplesheetfact_biosamplelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY hiseqsamplesheetfact
    ADD CONSTRAINT hiseqsamplesheetfact_biosamplelist_fkey FOREIGN KEY (biosamplelist) REFERENCES biosamplelist(obid);



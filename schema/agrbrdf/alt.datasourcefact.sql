--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcefact
    ADD CONSTRAINT "$1" FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);



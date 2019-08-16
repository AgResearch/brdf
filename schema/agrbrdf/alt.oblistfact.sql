--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY oblistfact
    ADD CONSTRAINT "$1" FOREIGN KEY (listob) REFERENCES oblist(obid);



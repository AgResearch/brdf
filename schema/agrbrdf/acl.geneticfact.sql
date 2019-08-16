--
-- Name: geneticfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticfact FROM agrbrdf;
GRANT ALL ON TABLE geneticfact TO agrbrdf;
GRANT SELECT ON TABLE geneticfact TO gbs;



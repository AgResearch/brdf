--
-- Name: geneticlocationfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticlocationfact FROM PUBLIC;
REVOKE ALL ON TABLE geneticlocationfact FROM agrbrdf;
GRANT ALL ON TABLE geneticlocationfact TO agrbrdf;
GRANT SELECT ON TABLE geneticlocationfact TO gbs;


